"""Reading the vault as files: one note, or every note.

This is the read shape shared by the lint report and the web reading view — both need
a note's frontmatter, body, aliases and raw YAML block, which is more than the indexing
:class:`~vault_spider.corpus.loader.Note` carries. :class:`VaultNote` satisfies the
:class:`~vault_spider.corpus.links.LinkNode` protocol, so it feeds the link graph directly.

Skip policy is the loader's, not a second one: a note tagged `#ignore`/`#secret`, an
Excalidraw drawing, or anything under a skipped or hidden directory is not a note here
either. :func:`read_note` returns ``None`` for those, which is what keeps a secret-tagged
note unreadable through any caller that goes through this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from vault_spider.corpus.frontmatter import (
    alias_list,
    coerce_datetime,
    frontmatter_text,
    normalize_tags,
    split_frontmatter,
)
from vault_spider.corpus.loader import (
    EXCALIDRAW_SUFFIX,
    has_ignore_frontmatter_tag,
    has_ignore_tag,
    is_excalidraw,
    is_skipped_path,
)
from vault_spider.utils import validate_vault_relative_path


@dataclass
class VaultNote:
    """A note read from disk, with everything link resolution and rendering need."""

    path: str  # vault-relative posix
    stem: str
    title: str
    frontmatter: Dict[str, Any]
    frontmatter_text: str  # raw YAML block, for links declared in frontmatter
    body: str
    note_type: str
    provenance: str = ""
    aliases: List[str] = field(default_factory=list)
    recency: Optional[datetime] = field(default=None)

    @property
    def tags(self) -> List[str]:
        return normalize_tags(self.frontmatter.get("tags"))


def note_recency(frontmatter: Dict[str, Any]) -> Optional[datetime]:
    for key in ("updated", "date", "created"):
        resolved = coerce_datetime(frontmatter.get(key))
        if resolved is not None:
            return resolved
    return None


def iter_note_files(root: Path) -> Iterator[Tuple[Path, str]]:
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if is_skipped_path(rel):
            continue
        yield path, rel.as_posix()


def iter_attachment_files(root: Path) -> Iterable[str]:
    """Vault-relative paths of every linkable file that is not an indexed note.

    That means real attachments (images, PDFs, ...) plus Excalidraw drawings: those are
    `.md` files, but they are skipped as notes, and a link to one still resolves in
    Obsidian — so it must not be reported broken.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if is_skipped_path(rel):
            continue
        if path.suffix.lower() == ".md" and not rel.name.lower().endswith(EXCALIDRAW_SUFFIX):
            continue
        yield rel.as_posix()


def build_note(relative_posix: str, raw: str) -> Optional[VaultNote]:
    """Parse one note's text, or return ``None`` when vault policy skips it."""
    frontmatter, body = split_frontmatter(raw)
    if has_ignore_tag(body) or has_ignore_frontmatter_tag(
        normalize_tags(frontmatter.get("tags"))
    ):
        return None
    if is_excalidraw(Path(relative_posix), frontmatter):
        return None
    stem = Path(relative_posix).stem
    return VaultNote(
        path=relative_posix,
        stem=stem,
        title=str(frontmatter.get("title") or stem),
        frontmatter=frontmatter,
        frontmatter_text=frontmatter_text(raw),
        body=body,
        note_type=str(frontmatter.get("type") or ""),
        provenance=str(frontmatter.get("provenance") or "").strip().lower(),
        aliases=alias_list(frontmatter.get("aliases")),
        recency=note_recency(frontmatter),
    )


def load_vault_notes(root: str) -> Tuple[List[VaultNote], int]:
    """Every readable note in the vault, plus how many were skipped by policy."""
    root_path = Path(root)
    notes: List[VaultNote] = []
    ignored = 0
    for path, rel in iter_note_files(root_path):
        try:
            raw = path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            # Same policy as the loader: skip files that are not valid UTF-8 rather
            # than reading silently mangled text.
            continue
        note = build_note(rel, raw)
        if note is None:
            ignored += 1
            continue
        notes.append(note)
    return notes, ignored


def read_note(root: str, relative_path: str) -> Optional[VaultNote]:
    """Read a single note by vault-relative path.

    Returns ``None`` when the file is missing, unreadable, or skipped by vault policy —
    all of which a caller should treat identically, so that an ignored note is
    indistinguishable from one that does not exist.

    Raises ``ValueError`` if ``relative_path`` is not a clean vault-relative POSIX path.
    """
    rel = validate_vault_relative_path(relative_path, label="path")
    if not rel.lower().endswith(".md") or is_skipped_path(Path(rel)):
        return None
    full = Path(root) / rel
    # `validate_vault_relative_path` already rejects `..`, but a symlink inside the vault
    # can still point outside it. Resolving both ends closes that on a networked server.
    try:
        root_real = Path(root).resolve(strict=True)
        if not full.resolve(strict=True).is_relative_to(root_real):
            return None
    except OSError:
        return None
    try:
        raw = full.read_text(encoding="utf-8", errors="strict")
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError, UnicodeDecodeError):
        return None
    return build_note(rel, raw)
