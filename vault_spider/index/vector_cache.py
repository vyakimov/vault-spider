"""Embedding vectors stored as files inside the vault, so the vault's own file sync carries them.

One machine embeds; it *exports* every vector of its index after each successful
sync. Other machines *import*: their ``sync`` takes vectors from these files and
never calls the embedding API (``index.vector_cache_mode``).

Layout, under ``<vault>/<index.vector_cache_dir>/<model slug>/``::

    manifest.json               model, dimensions, format, written last
    ab/abcdef0123….vec          one vector: little-endian float32, nothing else

Files are content-addressed and immutable. A vector's name is the ``entry_hash``
(sha256 of the exact embedded text), so a file is only ever created or deleted,
never rewritten. That suits file-sync services that keep a version history (and
count it against a quota): an edit to one note touches a few ~12 KB files. A
vector is valid only for the text that produced it, so a vector can never be
paired with the wrong text: a note whose text changed just finds no file yet. Each
model has its own directory, so vectors from two models never mix, even mid-sync.

Writes go through a hidden staging directory and an atomic rename, so a reader
(or a sync client, which skips dot-folders) never sees a partial file. Readers
still validate size and values: a file synced only partly reads as missing.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import tempfile
from array import array
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

FORMAT_VERSION = 1
MANIFEST = "manifest.json"
SUFFIX = ".vec"
_HASH = re.compile(r"^[0-9a-f]{64}$")


class VectorCacheError(ValueError):
    """The cache is unusable for this index (missing, wrong model, malformed)."""


def model_slug(model: str) -> str:
    """A directory name for a model id: ``google/gemini-embedding-2`` -> ``google_gemini-embedding-2``."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", model.strip()).strip("._")
    if not slug:
        raise VectorCacheError(f"cannot derive a directory name from model {model!r}")
    return slug


def exact_model_match(first: str, second: str) -> bool:
    return first == second


class VectorCache:
    """One model's vectors in one directory."""

    def __init__(self, directory: Path, model: str, dimensions: int):
        self.directory = Path(directory)
        self.model = model
        self.dimensions = dimensions

    # -- paths ---------------------------------------------------------------

    def path_for(self, entry_hash: str) -> Path:
        if not _HASH.match(entry_hash):
            raise VectorCacheError(f"not an entry hash: {entry_hash!r}")
        return self.directory / entry_hash[:2] / f"{entry_hash}{SUFFIX}"

    def _staging(self) -> Path:
        # A dot-folder: sync clients skip it, and the vault loader never reads it.
        return self.directory.parent / ".staging"

    def stored_hashes(self) -> Iterator[str]:
        if not self.directory.is_dir():
            return
        for shard in self.directory.iterdir():
            if not shard.is_dir() or len(shard.name) != 2:
                continue
            for path in shard.iterdir():
                name = path.name
                if name.endswith(SUFFIX) and _HASH.match(name[: -len(SUFFIX)]):
                    yield name[: -len(SUFFIX)]

    # -- reading -------------------------------------------------------------

    def get(self, entry_hash: str) -> Optional[List[float]]:
        """The vector for ``entry_hash``, or ``None`` if absent, partial or invalid."""
        try:
            payload = self.path_for(entry_hash).read_bytes()
        except (OSError, VectorCacheError):
            return None
        if len(payload) != self.dimensions * 4:
            return None
        values = array("f")
        values.frombytes(payload)
        if sys.byteorder != "little":  # pragma: no cover - all supported hosts are little-endian
            values.byteswap()
        vector = values.tolist()
        if not all(math.isfinite(value) for value in vector) or not any(vector):
            return None
        return vector

    # -- writing (the exporting machine) --------------------------------------

    def _write_atomic(self, destination: Path, payload: bytes) -> None:
        staging = self._staging()
        staging.mkdir(parents=True, exist_ok=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(dir=staging, delete=False)
        temporary = Path(handle.name)
        try:
            with handle:
                handle.write(payload)
            os.replace(temporary, destination)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise

    def export(self, vectors: Dict[str, List[float]], extra: Dict[str, Any]) -> Dict[str, int]:
        """Make the directory hold exactly ``vectors``; returns counts.

        New vectors are written first and stale ones deleted next. The manifest
        is written last, and only when it changes.
        """
        for entry_hash, vector in vectors.items():
            if len(vector) != self.dimensions:
                raise VectorCacheError(
                    f"vector {entry_hash[:12]}… has {len(vector)} dimensions, "
                    f"expected {self.dimensions}"
                )
        present = set(self.stored_hashes())
        written = 0
        for entry_hash in sorted(set(vectors) - present):
            values = array("f", vectors[entry_hash])
            if sys.byteorder != "little":  # pragma: no cover
                values.byteswap()
            self._write_atomic(self.path_for(entry_hash), values.tobytes())
            written += 1
        deleted = 0
        for entry_hash in sorted(present - set(vectors)):
            self.path_for(entry_hash).unlink(missing_ok=True)
            deleted += 1
        for shard in self.directory.iterdir() if self.directory.is_dir() else []:
            if shard.is_dir() and not any(shard.iterdir()):
                shard.rmdir()
        manifest = {
            "format_version": FORMAT_VERSION,
            "embedding_model": self.model,
            "dimensions": self.dimensions,
            "dtype": "float32-le",
            **extra,
        }
        manifest_path = self.directory / MANIFEST
        payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if not manifest_path.is_file() or manifest_path.read_bytes() != payload:
            self._write_atomic(manifest_path, payload)
        return {"written": written, "deleted": deleted, "total": len(vectors)}


def _read_manifest(directory: Path) -> Optional[Dict[str, Any]]:
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return manifest if isinstance(manifest, dict) else None


def for_export(root_dir: Path, model: str, dimensions: int) -> VectorCache:
    return VectorCache(Path(root_dir) / model_slug(model), model, dimensions)


def for_import(
    root_dir: Path,
    model: str,
    models_match: Callable[[str, str], bool] = exact_model_match,
) -> Tuple[Optional[VectorCache], Dict[str, Any]]:
    """The cache whose manifest names ``model`` (or an equivalent), if any.

    Returns ``(None, info)`` when no export has arrived yet. That isn't an
    error: sync then adds nothing new and reports every changed note as pending.
    """
    root_dir = Path(root_dir)
    found: List[Tuple[Path, Dict[str, Any]]] = []
    seen_models: List[str] = []
    for directory in sorted(root_dir.iterdir()) if root_dir.is_dir() else []:
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        manifest = _read_manifest(directory)
        if manifest is None:
            continue
        exported_model = str(manifest.get("embedding_model", ""))
        seen_models.append(exported_model)
        if models_match(exported_model, model):
            found.append((directory, manifest))
    if not found:
        return None, {"available_models": seen_models}
    if len(found) > 1:
        raise VectorCacheError(
            "more than one vector export matches the embedding model: "
            + ", ".join(str(directory) for directory, _ in found)
        )
    directory, manifest = found[0]
    if manifest.get("format_version") != FORMAT_VERSION:
        raise VectorCacheError(
            f"{directory / MANIFEST}: unsupported format_version {manifest.get('format_version')!r}"
        )
    dimensions = manifest.get("dimensions")
    if not isinstance(dimensions, int) or isinstance(dimensions, bool) or dimensions < 1:
        raise VectorCacheError(f"{directory / MANIFEST}: invalid dimensions {dimensions!r}")
    cache = VectorCache(directory, str(manifest["embedding_model"]), dimensions)
    return cache, manifest

