"""Build and maintain a Chroma collection for Markdown notes.

One note contributes one ``document``-granularity entry plus N ``section``
entries. Both live in a single collection, distinguished by the ``granularity``
metadata field.
"""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Set, Tuple, cast

import chromadb
from chromadb.errors import NotFoundError
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi

from vault_spider.config import BM25_CONFIG
from vault_spider.corpus.chunker import (
    CHUNK_SCHEMA_VERSION,
    Section,
    document_source_offset,
    document_text,
    section_source_offset,
    section_text,
    split_sections,
)
from vault_spider.corpus.links import build_link_graph
from vault_spider.corpus.loader import Note, load_notes
from vault_spider.index import graph as graph_index
from vault_spider.index.context_generator import (
    ContextualConfig,
    OpenRouterSummaryGenerator,
    SummaryGenerationError,
)
from vault_spider.index.context_summaries import (
    SUMMARY_SCHEMA_VERSION,
    SummaryResolution,
    SummaryStore,
)
from vault_spider.llm.openrouter import OpenRouterClient, OpenRouterError
from vault_spider.utils import DEFAULT_STOP_WORDS, tokenize_for_bm25

GRANULARITIES = ("document", "section")


class IndexConfigError(ValueError):
    """Stored index metadata is incompatible with the requested configuration."""


class IndexStore:
    """Maintain the persistent vector store and in-memory BM25 indexes."""

    def __init__(
        self,
        chroma_db_path: str = "chroma_db",
        collection_name: str = "vault_notes",
        bm25_k1: Optional[float] = None,
        bm25_b: Optional[float] = None,
        provider: Optional[OpenRouterClient] = None,
        allow_model_mismatch: bool = False,
        contextual: Optional[ContextualConfig] = None,
    ):
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.provider = provider or OpenRouterClient.from_env()
        # True when the caller intends to reset the collection anyway (sync
        # --reset); an embedding-model mismatch is then not an error.
        self.allow_model_mismatch = allow_model_mismatch
        self.contextual = contextual or ContextualConfig.from_settings(self.provider)
        if self.contextual.source not in {"manual", "openrouter"}:
            raise IndexConfigError(
                "context source must be 'manual' or 'openrouter'"
            )
        if (
            self.contextual.enabled
            and not self.contextual.path
        ):
            raise IndexConfigError("contextual retrieval requires a context path")
        self.summary_store: Optional[SummaryStore] = None
        self.summary_generator: Optional[OpenRouterSummaryGenerator] = None
        if self.contextual.enabled:
            self.summary_store = SummaryStore(self.contextual.path)
            if self.contextual.source == "openrouter":
                self.summary_generator = OpenRouterSummaryGenerator(
                    self.provider,
                    self.contextual,
                )
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        self.bm25_k1 = BM25_CONFIG["k1"] if bm25_k1 is None else bm25_k1
        self.bm25_b = BM25_CONFIG["b"] if bm25_b is None else bm25_b
        self.stop_words = DEFAULT_STOP_WORDS
        self.stemmer = PorterStemmer()

        # Per-granularity in-memory state.
        self.documents: Dict[str, List[str]] = {g: [] for g in GRANULARITIES}
        self.lexical_documents: Dict[str, List[str]] = {
            g: [] for g in GRANULARITIES
        }
        self.source_documents: Dict[str, List[str]] = {
            g: [] for g in GRANULARITIES
        }
        self.ids: Dict[str, List[str]] = {g: [] for g in GRANULARITIES}
        self.metadatas: Dict[str, List[Dict[str, Any]]] = {
            g: [] for g in GRANULARITIES
        }
        self.tokenized: Dict[str, List[List[str]]] = {g: [] for g in GRANULARITIES}
        self.bm25: Dict[str, Optional[BM25Okapi]] = {g: None for g in GRANULARITIES}
        self.graph_outgoing: Dict[str, Set[str]] = {}
        self.graph_incoming: Dict[str, Set[str]] = {}
        self.graph_status = "missing"
        self.graph_schema_version: int | None = None

        self.collection = self._load_or_create_collection()
        self._rehydrate_from_collection()

    # -- collection lifecycle -------------------------------------------------

    def _context_model(self) -> str:
        if not self.contextual.enabled:
            return ""
        return (
            "manual"
            if self.contextual.source == "manual"
            else self.contextual.model
        )

    def _context_version(self) -> int:
        return SUMMARY_SCHEMA_VERSION

    def _context_eligible(self, sections: List[Section]) -> bool:
        return bool(sections)

    def _collection_metadata(self) -> Dict[str, str]:
        return {
            "description": "Vault note embeddings",
            "provider": "openrouter",
            "embedding_model": self.provider.embedding_model,
            "chunk_schema_version": str(CHUNK_SCHEMA_VERSION),
            "contextual_state": "on" if self.contextual.enabled else "off",
            "context_source": (
                self.contextual.source if self.contextual.enabled else "off"
            ),
            "context_model": self._context_model(),
            "context_prompt_version": str(self._context_version()),
        }

    def _load_or_create_collection(self):
        # The mismatch check must stay outside the try: raising it inside would
        # fall through to create_collection on an existing name and surface as
        # a confusing "collection already exists" error instead.
        try:
            collection = self.client.get_collection(name=self.collection_name)
        except (ValueError, NotFoundError):
            return self.client.create_collection(
                name=self.collection_name,
                metadata=self._collection_metadata(),
            )
        current_metadata = getattr(collection, "metadata", None) or {}
        existing_model = current_metadata.get("embedding_model")
        if (
            existing_model
            and existing_model != self.provider.embedding_model
            and not self.allow_model_mismatch
        ):
            raise IndexConfigError(
                "Collection was built with a different embedding model. "
                "Run `vault-spider sync --reset` to rebuild it."
            )
        if (
            current_metadata.get("contextual_state") == "on"
            and not self.contextual.enabled
            and not self.allow_model_mismatch
        ):
            raise IndexConfigError(
                "Collection contains contextual embeddings but index.contextual is false. "
                "Run `vault-spider sync --reset` to rebuild it without generated context."
            )
        return collection

    def _reset_collection(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except (ValueError, NotFoundError):
            pass
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata=self._collection_metadata(),
        )

    # -- in-memory rehydration ------------------------------------------------

    def _tokenize(self, documents: List[str]) -> List[List[str]]:
        return [
            tokenize_for_bm25(document, self.stop_words, self.stemmer)
            for document in documents
        ]

    def _rehydrate_from_collection(self) -> None:
        for granularity in GRANULARITIES:
            self.documents[granularity] = []
            self.lexical_documents[granularity] = []
            self.source_documents[granularity] = []
            self.ids[granularity] = []
            self.metadatas[granularity] = []
            self.tokenized[granularity] = []
            self.bm25[granularity] = None

        if self.collection.count() > 0:
            payload = self.collection.get(include=["documents", "metadatas"])
            all_ids = payload.get("ids") or []
            all_documents = payload.get("documents") or []
            all_metadatas = payload.get("metadatas") or []

            for entry_id, document, metadata in zip(all_ids, all_documents, all_metadatas):
                metadata_dict: Dict[str, Any] = dict(metadata)
                granularity = str(metadata_dict.get("granularity", "document"))
                if granularity not in self.documents:
                    granularity = "document"
                self.ids[granularity].append(entry_id)
                self.documents[granularity].append(document)
                source_offset = int(str(metadata_dict.get("source_offset", 0) or 0))
                source = document[source_offset:] if source_offset else document
                self.source_documents[granularity].append(source)
                self.lexical_documents[granularity].append(
                    self._lexical_text(document, metadata_dict, source)
                )
                self.metadatas[granularity].append(metadata_dict)

        self._rehydrate_graph()

    def _rehydrate_graph(self) -> None:
        snapshot = graph_index.resolve(
            self.metadatas["document"], getattr(self.collection, "metadata", None)
        )
        self.graph = snapshot
        self.graph_outgoing = snapshot.outgoing
        self.graph_incoming = snapshot.incoming
        self.graph_status = snapshot.status
        self.graph_schema_version = snapshot.schema_version

    def graph_neighbors(self, note_id: str) -> Set[str]:
        """Symmetric one-hop neighbors, disabled when graph integrity is not okay."""
        if self.graph_status != "ok":
            return set()
        return set(self.graph_outgoing.get(note_id, set())) | set(
            self.graph_incoming.get(note_id, set())
        )

    def graph_degree(self, note_id: str) -> int:
        return len(self.graph_neighbors(note_id))

    def _graph_report(self) -> Dict[str, object]:
        # Reads `self.graph_status` rather than the snapshot's, so the attribute stays
        # the single switch that disables expansion.
        return {
            "graph_status": self.graph_status,
            "graph_nodes": len(self.graph_outgoing),
            "graph_edges": graph_index.edge_count(self.graph_outgoing),
            "graph_schema_version": self.graph_schema_version,
        }

    def _ensure_bm25(self, granularity: str) -> None:
        if self.bm25[granularity] is not None or not self.lexical_documents[granularity]:
            return
        self.tokenized[granularity] = self._tokenize(
            self.lexical_documents[granularity]
        )
        self.bm25[granularity] = BM25Okapi(
            self.tokenized[granularity], k1=self.bm25_k1, b=self.bm25_b
        )

    def granularity_data(
        self, granularity: str
    ) -> Tuple[List[str], List[str], List[Dict[str, Any]], Optional[BM25Okapi]]:
        self._ensure_bm25(granularity)
        return (
            self.documents[granularity],
            self.ids[granularity],
            self.metadatas[granularity],
            self.bm25[granularity],
        )

    def _lexical_text(
        self,
        document: str,
        metadata: Dict[str, Any],
        source: str,
    ) -> str:
        """BM25 text: the baseline header plus the raw body.

        The note summary is excluded unless index.contextual_bm25 is set. A
        per-note summary is identical across all of that note's sections, so
        feeding it to BM25 both distorts length normalisation and makes the
        sections lexically indistinguishable from one another.
        """
        lines = [f"# {metadata.get('title', '')}"]
        if metadata.get("granularity") == "document":
            lines.append(f"Path: {metadata.get('path', '')}")
            if metadata.get("tags"):
                lines.append(f"Tags: {metadata['tags']}")
            if metadata.get("date"):
                lines.append(f"Date: {metadata['date']}")
            if self.contextual.contextual_bm25 and metadata.get("context"):
                lines.append(f"Note summary: {metadata['context']}")
            return "\n\n".join(lines + [source]).strip()
        lines.append(f"Section: {metadata.get('heading') or '(intro)'}")
        if self.contextual.contextual_bm25 and metadata.get("context"):
            lines.append(f"Note summary: {metadata['context']}")
        return "\n\n".join(lines) + "\n\n" + source

    # -- entry assembly -------------------------------------------------------

    def _base_metadata(self, note: Note) -> Dict[str, Any]:
        folder = PurePosixPath(note.path).parent.as_posix()
        return {
            "note_id": note.note_id,
            "title": note.title,
            "path": note.path,
            "folder": folder,
            "tags": ", ".join(note.tags),
            "date": note.date,
            "created": note.created or "",
            "updated": note.updated or "",
            "note_type": note.note_type,
            "provenance": note.provenance,
            "content_hash": note.content_hash,
            "source": "vault_markdown",
        }

    def _entries_for_note(
        self,
        note: Note,
        graph_outgoing: Set[str],
        sections: Optional[List[Section]] = None,
        contexts: Optional[Dict[str, str]] = None,
        context_input_hashes: Optional[Dict[str, str]] = None,
        context_status: Optional[str] = None,
        note_context: str = "",
        note_context_key: str = "",
        note_context_model: str = "",
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        entries: List[Tuple[str, str, Dict[str, Any]]] = []
        sections = split_sections(note) if sections is None else sections
        contexts = contexts or {}
        context_input_hashes = context_input_hashes or {}
        context_eligible = self._context_eligible(sections)
        context_label = "Note summary"
        resolved_status = context_status or (
            "disabled"
            if context_eligible
            else "not_needed"
        )

        doc_metadata = self._base_metadata(note)
        document_context = note_context if self.contextual.enabled else ""
        document_status = (
            resolved_status
            if self.contextual.enabled
            else "not_needed"
        )
        doc_metadata.update(
            {
                "granularity": "document",
                "heading": "",
                "heading_path": "",
                "parent_section_id": "",
                "line_start": 0,
                "line_end": 0,
                "graph_outgoing": graph_index.encode_outgoing(graph_outgoing),
                "chunk_schema_version": CHUNK_SCHEMA_VERSION,
                "source_offset": document_source_offset(
                    note, document_context, context_label
                ),
                "context_eligible": False,
                "context_status": document_status,
                "context": document_context,
                "context_source": (
                    "summary" if document_context else ""
                ),
                "context_model": note_context_model if document_context else "",
                "context_prompt_version": (
                    self._context_version() if document_context else 0
                ),
                "context_input_hash": note_context_key if document_context else "",
            }
        )
        doc_text = document_text(note, document_context, context_label)
        doc_metadata["entry_hash"] = hashlib.sha256(doc_text.encode("utf-8")).hexdigest()
        entries.append((f"{note.note_id}::doc", doc_text, doc_metadata))

        for section in sections:
            context = contexts.get(section.chunk_id, "")
            section_metadata = self._base_metadata(note)
            section_metadata.update(
                {
                    "granularity": "section",
                    "heading": section.heading,
                    # Location metadata only. Deliberately not part of the
                    # embedded or BM25 text: a wider provenance preamble was
                    # measured there and cost more than it returned.
                    "heading_path": " > ".join(section.heading_path),
                    "parent_section_id": section.parent_section_id,
                    "line_start": section.line_start,
                    "line_end": section.line_end,
                    "chunk_schema_version": CHUNK_SCHEMA_VERSION,
                    "source_offset": section_source_offset(
                        note, section, context, context_label
                    ),
                    "section_hash": hashlib.sha256(
                        section.text.encode("utf-8")
                    ).hexdigest(),
                    "token_count": section.token_count,
                    "context_eligible": context_eligible,
                    "context_status": (
                        resolved_status if context_eligible else "not_needed"
                    ),
                    "context": context,
                    "context_source": "summary" if context else "",
                    "context_model": note_context_model if context else "",
                    "context_prompt_version": (
                        self._context_version() if context else 0
                    ),
                    "context_input_hash": context_input_hashes.get(
                        section.chunk_id, ""
                    ),
                }
            )
            text = section_text(
                note,
                section,
                context,
                context_label,
            )
            section_metadata["entry_hash"] = hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest()
            entries.append((section.chunk_id, text, section_metadata))
        return entries

    # -- sync -----------------------------------------------------------------

    def sync(
        self,
        root: str,
        reset: bool = False,
        dry_run: bool = False,
        contextualize: bool = False,
        refresh_context: bool = False,
    ) -> Dict[str, object]:
        if reset and dry_run:
            # Reset drops the collection before anything is predicted; a
            # "dry run" that destroys data must be impossible.
            raise ValueError("reset cannot be combined with dry_run")
        if (contextualize or refresh_context) and not self.contextual.enabled:
            raise ValueError(
                "--contextualize and --refresh-context require index.contextual: true"
            )
        if refresh_context and self.contextual.source == "manual":
            raise ValueError(
                "--refresh-context is only available with index.context_source: "
                "openrouter; prepare and import a new manual summary instead"
            )
        if refresh_context:
            contextualize = True
        if reset:
            self._reset_collection()

        notes = load_notes(root)
        warnings: List[str] = []

        # Two files sharing a frontmatter id would collide on entry ids; index
        # the first (load_notes is path-sorted) and skip the rest.
        seen_note_ids: Dict[str, str] = {}
        deduped: List[Note] = []
        for note in notes:
            first_path = seen_note_ids.get(note.note_id)
            if first_path is not None:
                warnings.append(
                    f"duplicate note id {note.note_id}: skipped {note.path} "
                    f"(already used by {first_path})"
                )
                continue
            seen_note_ids[note.note_id] = note.path
            deduped.append(note)
        notes = deduped

        # The index discards unresolved links and never reads attachment bookkeeping.
        # Avoid walking the entire vault tree just to resolve attachment-only links.
        path_graph = build_link_graph(notes, ())
        note_id_by_path = {note.path: note.note_id for note in notes}
        desired_graph_outgoing: Dict[str, Set[str]] = {
            note.note_id: {
                note_id_by_path[target_path]
                for target_path in path_graph.outgoing.get(note.path, set())
                if target_path in note_id_by_path
            }
            for note in notes
        }
        existing = self.collection.get(include=["metadatas"])
        existing_ids = existing.get("ids") or []
        existing_metas = existing.get("metadatas") or []
        existing_by_note: Dict[str, Dict[str, Any]] = {}
        existing_documents: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        for entry_id, metadata in zip(existing_ids, existing_metas):
            note_id = str(metadata.get("note_id", ""))
            if metadata.get("granularity", "document") == "document":
                existing_documents.setdefault(note_id, (entry_id, dict(metadata)))
            group = existing_by_note.setdefault(
                note_id,
                {
                    "ids": [],
                    "content_hash": metadata.get("content_hash", ""),
                    "path": metadata.get("path", ""),
                    "metadatas": [],
                },
            )
            group["ids"].append(entry_id)  # type: ignore[union-attr]
            group["metadatas"].append(metadata)  # type: ignore[union-attr]

        ids_to_delete: List[str] = []
        entries_to_add: List[Tuple[str, str, Dict[str, Any]]] = []
        would_add: List[str] = []
        would_update: List[str] = []
        would_delete: List[str] = []
        would_rechunk: List[str] = []
        would_contextualize: List[str] = []
        would_refresh_context: List[str] = []
        reusable: Dict[str, List[float]] = {}
        planned_adds = planned_updates = deleted_notes = unchanged = 0
        action_plans: List[
            Tuple[Note, List[Section], Optional[Dict[str, Any]], str]
        ] = []
        sections_by_note: Dict[str, List[Section]] = {}
        summary_resolutions: Dict[str, SummaryResolution] = {}
        # Notes whose entries are fully rewritten this sync; the graph metadata
        # patch below skips them because their new entries already carry it.
        rewritten_note_ids: Set[str] = set()

        disk_note_ids = set()
        for note in notes:
            disk_note_ids.add(note.note_id)
            sections = split_sections(note)
            sections_by_note[note.note_id] = sections
            group = existing_by_note.get(note.note_id)
            eligible = self.contextual.enabled and self._context_eligible(sections)
            summary_resolution: Optional[SummaryResolution] = None
            if self.contextual.enabled:
                if self.summary_store is None:
                    raise RuntimeError("summary store is unavailable")
                summary_resolution = self.summary_store.resolve(note)
                summary_resolutions[note.note_id] = summary_resolution
            if group is None:
                would_add.append(note.path)
                planned_adds += 1
                action_plans.append((note, sections, None, "add"))
                if eligible and (
                    self.contextual.source == "openrouter"
                    or summary_resolution is not None
                    and summary_resolution.status == "ready"
                ):
                    would_contextualize.append(note.path)
                continue

            raw_group_metas = group.get("metadatas")
            group_metas = (
                [metadata for metadata in raw_group_metas if isinstance(metadata, dict)]
                if isinstance(raw_group_metas, list)
                else []
            )
            structurally_stale = any(
                int(str(metadata.get("chunk_schema_version", 0) or 0))
                != CHUNK_SCHEMA_VERSION
                for metadata in group_metas
            )
            if summary_resolution is not None:
                expected_status = summary_resolution.status
                expected_key = (
                    summary_resolution.context_key
                    if summary_resolution.status == "ready"
                    else ""
                )
                context_stale = any(
                    metadata.get("context_status") != expected_status
                    or metadata.get("context_source")
                    != (
                        "summary"
                        if summary_resolution.status == "ready"
                        else ""
                    )
                    or str(metadata.get("context_input_hash", ""))
                    != expected_key
                    for metadata in group_metas
                    if metadata.get("granularity") == "document"
                    or eligible
                )
            else:
                context_stale = False
            changed = (
                group.get("content_hash") != note.content_hash
                or group.get("path") != note.path
            )
            context_requested = context_stale or (
                self.contextual.enabled
                and self.contextual.source == "openrouter"
                and (
                    refresh_context
                    or summary_resolution is not None
                    and summary_resolution.status != "ready"
                )
            )
            if changed or structurally_stale or context_requested:
                would_update.append(note.path)
                planned_updates += 1
                reason = (
                    "refresh"
                    if refresh_context and eligible
                    else "context"
                    if context_requested
                    else "rechunk"
                    if structurally_stale and not changed
                    else "update"
                )
                action_plans.append((note, sections, group, reason))
                if structurally_stale:
                    would_rechunk.append(note.path)
                if eligible and (
                    self.contextual.source == "openrouter"
                    or summary_resolution is not None
                    and summary_resolution.status == "ready"
                ):
                    would_contextualize.append(note.path)
                    if refresh_context:
                        would_refresh_context.append(note.path)
            else:
                unchanged += 1

        for note_id, group in existing_by_note.items():
            if note_id not in disk_note_ids:
                ids_to_delete.extend(group["ids"])  # type: ignore[arg-type]
                would_delete.append(str(group.get("path") or note_id))
                deleted_notes += 1

        graph_update_ids: List[str] = []
        graph_update_metas: List[Dict[str, object]] = []
        graph_records_changed = 0
        for note in notes:
            desired_encoded = graph_index.encode_outgoing(
                desired_graph_outgoing[note.note_id]
            )
            existing_document = existing_documents.get(note.note_id)
            existing_encoded = (
                existing_document[1].get("graph_outgoing")
                if existing_document is not None
                else None
            )
            if existing_encoded == desired_encoded:
                continue
            graph_records_changed += 1
            if (
                existing_document is not None
                and note.note_id not in rewritten_note_ids
            ):
                entry_id, metadata = existing_document
                complete_metadata = dict(metadata)
                complete_metadata["graph_outgoing"] = desired_encoded
                graph_update_ids.append(entry_id)
                graph_update_metas.append(complete_metadata)

        if dry_run:
            return {
                "added_notes": planned_adds,
                "updated_notes": planned_updates,
                "deleted_notes": deleted_notes,
                "unchanged": unchanged,
                "total_entries": self.collection.count(),
                "graph_records_changed": graph_records_changed,
                "warnings": warnings,
                "dry_run": True,
                "would_add": sorted(would_add),
                "would_update": sorted(would_update),
                "would_delete": sorted(would_delete),
                "would_rechunk": sorted(would_rechunk),
                "would_contextualize": sorted(set(would_contextualize)),
                "would_refresh_context": sorted(set(would_refresh_context)),
                "context": self._context_summary(
                    notes,
                    sections_by_note,
                    generated=0,
                    summary_hits=0,
                    failed_notes=[],
                ),
                **self._graph_report(),
            }

        generated = summary_hits = 0
        failed_notes: List[str] = []
        added_notes = updated_notes = 0
        for note, sections, group, reason in action_plans:
            contexts: Dict[str, str] = {}
            input_hashes: Dict[str, str] = {}
            context_status: Optional[str] = None
            note_context = ""
            note_context_key = ""
            note_context_model = ""
            if self.contextual.enabled:
                resolution = summary_resolutions[note.note_id]
                if self.contextual.source == "openrouter" and (
                    refresh_context or resolution.status != "ready"
                ):
                    if self.summary_generator is None or self.summary_store is None:
                        raise RuntimeError("OpenRouter summary generator is unavailable")
                    try:
                        record = self.summary_generator.generate(note)
                        self.summary_store.put_many([record])
                        resolution = self.summary_store.resolve(note)
                        summary_resolutions[note.note_id] = resolution
                        generated += 1
                    except (SummaryGenerationError, OpenRouterError) as exc:
                        failed_notes.append(note.path)
                        warnings.append(
                            f"summary generation failed for {note.path}: {exc}"
                        )
                context_status = resolution.status
                if resolution.status == "ready":
                    note_context = resolution.summary
                    note_context_key = resolution.context_key
                    if resolution.record is not None:
                        note_context_model = (
                            resolution.record.generator_model
                            or resolution.record.generated_by
                        )
                    contexts = {
                        section.chunk_id: resolution.summary
                        for section in sections
                    }
                    input_hashes = {
                        section.chunk_id: resolution.context_key
                        for section in sections
                    }
                    summary_hits += 1

            if group is not None:
                old = self.collection.get(
                    ids=cast(List[str], group["ids"]),
                    include=["embeddings", "metadatas"],
                )
                old_embeddings = old.get("embeddings")
                for embedding, metadata in zip(
                    [] if old_embeddings is None else old_embeddings,
                    old.get("metadatas") or [],
                ):
                    entry_hash = str(metadata.get("entry_hash", ""))
                    if entry_hash and embedding is not None:
                        reusable[entry_hash] = [float(value) for value in embedding]
                ids_to_delete.extend(group["ids"])  # type: ignore[arg-type]
                updated_notes += 1
            else:
                added_notes += 1
            rewritten_note_ids.add(note.note_id)
            entries_to_add.extend(
                self._entries_for_note(
                    note,
                    desired_graph_outgoing[note.note_id],
                    sections,
                    contexts,
                    input_hashes,
                    context_status=context_status,
                    note_context=note_context,
                    note_context_key=note_context_key,
                    note_context_model=note_context_model,
                )
            )

        add_ids: List[str] = []
        add_texts: List[str] = []
        add_metas: List[Dict[str, Any]] = []
        resolved_embeddings: List[List[float]] = []
        if entries_to_add:
            add_ids = [entry[0] for entry in entries_to_add]
            add_texts = [entry[1] for entry in entries_to_add]
            add_metas = [entry[2] for entry in entries_to_add]
            embeddings: List[Optional[List[float]]] = [None] * len(entries_to_add)
            missing_indexes = []
            missing_texts = []
            for index, metadata in enumerate(add_metas):
                cached = reusable.get(str(metadata.get("entry_hash", "")))
                if cached is None:
                    missing_indexes.append(index)
                    missing_texts.append(add_texts[index])
                else:
                    embeddings[index] = cached
            if missing_texts:
                computed = self.provider.embed_texts(missing_texts, batch_size=32)
                if len(computed) != len(missing_indexes):
                    raise OpenRouterError(
                        f"Embedding provider returned {len(computed)} vectors "
                        f"for {len(missing_indexes)} entries"
                    )
                for index, embedding in zip(missing_indexes, computed):
                    embeddings[index] = embedding
            resolved_embeddings = [embedding for embedding in embeddings if embedding is not None]
            if len(resolved_embeddings) != len(entries_to_add):
                raise OpenRouterError("Embedding provider did not resolve every index entry")

        # Finish all fallible provider work before removing the old entries. A
        # transient embedding failure must leave the currently usable index
        # intact so the next sync can retry safely.
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

        if entries_to_add:
            self._add_in_batches(add_ids, add_texts, add_metas, resolved_embeddings)

        if graph_update_ids:
            self._update_metadatas_in_batches(graph_update_ids, graph_update_metas)

        graph_snapshot_hash = graph_index.snapshot_hash(desired_graph_outgoing)
        graph_edges = graph_index.edge_count(desired_graph_outgoing)
        # Chroma replaces collection metadata wholesale, so carry the existing
        # keys forward. The snapshot hash is written only after every entry write.
        collection_metadata = dict(self.collection.metadata or {})
        collection_metadata.update(self._collection_metadata())
        collection_metadata.update(
            {
                "graph_schema_version": graph_index.GRAPH_SCHEMA_VERSION,
                "graph_snapshot_hash": graph_snapshot_hash,
                "graph_nodes": len(desired_graph_outgoing),
                "graph_edges": graph_edges,
            }
        )
        self.collection.modify(metadata=collection_metadata)
        self._rehydrate_from_collection()

        return {
            "added_notes": added_notes,
            "updated_notes": updated_notes,
            "deleted_notes": deleted_notes,
            "unchanged": unchanged,
            "total_entries": self.collection.count(),
            "graph_records_changed": graph_records_changed,
            "warnings": warnings,
            "dry_run": False,
            "context": self._context_summary(
                notes,
                sections_by_note,
                generated=generated,
                summary_hits=summary_hits,
                failed_notes=failed_notes,
            ),
            **self._graph_report(),
        }

    def _context_summary(
        self,
        notes: List[Note],
        sections_by_note: Dict[str, List[Section]],
        *,
        generated: int,
        summary_hits: int,
        failed_notes: List[str],
    ) -> Dict[str, object]:
        eligible_ids = {
            note.note_id
            for note in notes
            if self._context_eligible(sections_by_note.get(note.note_id, []))
        }
        eligible_sections = sum(
            len(sections_by_note.get(note_id, [])) for note_id in eligible_ids
        )
        ready_sections = sum(
            metadata.get("note_id") in eligible_ids
            and metadata.get("context_status") == "ready"
            and metadata.get("context_source") == "summary"
            and int(str(metadata.get("context_prompt_version", 0) or 0))
            == self._context_version()
            for metadata in self.metadatas["section"]
        )
        missing_notes = stale_notes = 0
        if self.contextual.enabled and self.summary_store is not None:
            statuses = [self.summary_store.resolve(note).status for note in notes]
            missing_notes = statuses.count("missing")
            stale_notes = statuses.count("stale")
        stale_sections = (
            max(0, eligible_sections - ready_sections)
            if self.contextual.enabled
            else 0
        )
        return {
            "eligible_notes": len(eligible_ids),
            "eligible_sections": eligible_sections,
            "ready_sections": ready_sections,
            "stale_sections": stale_sections,
            "generated": generated,
            "summary_hits": summary_hits,
            "source": (
                self.contextual.source if self.contextual.enabled else "off"
            ),
            "missing_notes": missing_notes,
            "stale_notes": stale_notes,
            "failed_notes": sorted(failed_notes),
            "coverage": (
                round(ready_sections / eligible_sections, 4)
                if self.contextual.enabled and eligible_sections
                else 1.0
            ),
        }

    def _add_in_batches(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
        batch_size: int = 512,
    ) -> None:
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.add(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=cast(Any, metadatas[start:end]),
                embeddings=cast(Any, embeddings[start:end]),
            )

    def _update_metadatas_in_batches(
        self,
        ids: List[str],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 512,
    ) -> None:
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            self.collection.update(
                ids=ids[start:end],
                metadatas=cast(Any, metadatas[start:end]),
            )

    # -- stats ----------------------------------------------------------------

    def get_collection_stats(self) -> Dict[str, object]:
        document_metas = self.metadatas["document"]
        if not document_metas:
            return {
                "total_documents": 0,
                "total_entries": self.collection.count(),
                **self._graph_report(),
            }

        folders = set()
        tag_values = set()
        dated_notes = 0
        for metadata in document_metas:
            folder = metadata.get("folder")
            if folder:
                folders.add(folder)
            tags = metadata.get("tags")
            if tags:
                tag_values.update(
                    tag.strip() for tag in str(tags).split(",") if tag.strip()
                )
            if metadata.get("date"):
                dated_notes += 1

        return {
            "total_documents": len(document_metas),
            "total_entries": self.collection.count(),
            "section_entries": len(self.metadatas["section"]),
            "unique_folders": len(folders),
            "unique_tags": len(tag_values),
            "dated_notes": dated_notes,
            "embedding_model": self.provider.embedding_model,
            "chunk_schema_version": CHUNK_SCHEMA_VERSION,
            "context_prompt_version": self._context_version(),
            "context_model": self._context_model(),
            "context_source": (
                self.contextual.source if self.contextual.enabled else "off"
            ),
            "contextual_enabled": self.contextual.enabled,
            "contextual_bm25": self.contextual.contextual_bm25,
            "context_eligible_sections": sum(
                bool(metadata.get("context_eligible"))
                for metadata in self.metadatas["section"]
            ),
            "context_ready_sections": sum(
                metadata.get("context_status") == "ready"
                for metadata in self.metadatas["section"]
            ),
            **self._graph_report(),
        }
