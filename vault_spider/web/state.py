"""Process-wide singletons for the web app.

``IndexStore`` pulls every document out of Chroma to rebuild BM25 when it is constructed,
so it is built exactly once at startup and shared. The link graph needs a full vault walk,
so it is cached too and refreshed only when the vault's files change.

Everything here is blocking. Route handlers must stay sync ``def`` so Starlette runs them
in its threadpool rather than stalling the event loop.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from vault_spider import settings
from vault_spider.corpus.links import LinkGraph, build_link_graph
from vault_spider.corpus.vault import (
    VaultNote,
    iter_attachment_files,
    iter_note_files,
    load_vault_notes,
    read_note,
)
from vault_spider.index.store import IndexStore
from vault_spider.llm.openrouter import OpenRouterClient
from vault_spider.retrieval.searcher import Searcher


class StartupError(RuntimeError):
    """Raised when the app cannot serve: no vault, no index, no API key."""


@dataclass
class VaultSnapshot:
    """The vault as last walked: notes, link graph, and the signature that dated it."""

    notes: List[VaultNote]
    graph: LinkGraph
    signature: int
    by_path: Dict[str, VaultNote]


class AppState:
    """Everything a request needs, built once.

    Takes its collaborators rather than constructing them, so tests can hand it a fake
    provider and a temp index without reaching into the object.
    """

    def __init__(self, vault_root: str, provider, store: IndexStore, searcher: Searcher):
        self.vault_root = vault_root
        self.provider = provider
        self.store = store
        self.searcher = searcher
        self._snapshot: Optional[VaultSnapshot] = None
        self._lock = threading.Lock()

    @classmethod
    def connect(
        cls, vault_root: str, chroma_path: str, collection: str = "vault_notes"
    ) -> "AppState":
        """Build the real singletons: provider, store, searcher."""
        provider = OpenRouterClient.from_env()
        store = IndexStore(
            chroma_db_path=chroma_path, collection_name=collection, provider=provider
        )
        searcher = Searcher(store, granularity="document", provider=provider)
        return cls(vault_root=vault_root, provider=provider, store=store, searcher=searcher)

    # -- retrieval ---------------------------------------------------------

    def warm(self) -> None:
        """Build both BM25 pools up front.

        ``IndexStore._ensure_bm25`` fills shared dicts lazily, so two concurrent cold
        requests would each build the same index. Doing it once at startup removes both
        the race and the first-query stall.
        """
        for granularity in ("document", "section"):
            try:
                self.store.granularity_data(granularity)
            except Exception:  # noqa: BLE001 - a missing pool is not fatal to startup
                continue

    def stats(self) -> Dict[str, object]:
        return self.store.get_collection_stats()

    # -- vault -------------------------------------------------------------

    def _vault_signature(self) -> int:
        """A cheap fingerprint of the vault's note files.

        Hashing paths and mtimes costs one stat per note and catches every edit,
        addition and deletion — enough to know when the link graph is stale.
        """
        root = Path(self.vault_root)
        total = 0
        for path, rel in iter_note_files(root):
            try:
                total ^= hash((rel, path.stat().st_mtime_ns))
            except OSError:
                continue
        return total

    def snapshot(self) -> VaultSnapshot:
        """The current vault walk, rebuilt only when a note file has changed."""
        signature = self._vault_signature()
        with self._lock:
            if self._snapshot is not None and self._snapshot.signature == signature:
                return self._snapshot
            notes, _ignored = load_vault_notes(self.vault_root)
            graph = build_link_graph(notes, iter_attachment_files(Path(self.vault_root)))
            self._snapshot = VaultSnapshot(
                notes=notes,
                graph=graph,
                signature=signature,
                by_path={note.path: note for note in notes},
            )
            return self._snapshot

    def note(self, relative_path: str) -> Optional[VaultNote]:
        """Read one note from disk. ``None`` covers missing, unreadable and ignored."""
        return read_note(self.vault_root, relative_path)


def resolve_vault_root() -> str:
    """The vault to serve, pinned at startup.

    Deliberately does **not** fall back to Obsidian's active-vault registry: a server's
    idea of which vault it serves must not change because a desktop app switched windows.
    """
    root = settings.vault_root()
    if not root:
        raise StartupError(
            "No vault configured. Set `vault.root` in config.yaml — the web app will not "
            "fall back to Obsidian's active vault."
        )
    if not Path(root).is_dir():
        raise StartupError(f"Configured vault.root does not exist: {root}")
    return root


def build_state() -> AppState:
    """Construct the singletons, turning setup problems into readable failures."""
    root = resolve_vault_root()
    try:
        state = AppState.connect(vault_root=root, chroma_path=settings.chroma_path())
    except ValueError as exc:
        # Missing API key, or an index built with a different embedding model.
        raise StartupError(str(exc)) from exc
    if state.store.collection is None or state.store.collection.count() == 0:
        raise StartupError("The index is empty. Run `./bin/vault-spider sync` first.")
    state.warm()
    return state
