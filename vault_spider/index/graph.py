"""The persisted note-level wikilink graph: encoding, hashing, and integrity.

Both the writable index (:class:`~vault_spider.index.store.IndexStore`) and the
read-only :class:`~vault_spider.index.reader.DatabaseReader` have to answer "is this
collection's graph trustworthy?", and they must answer it identically — so the rules
live here rather than in either caller.

Edges are stored as a JSON list of target note ids on each *document*-granularity
entry, and the collection carries a hash of the whole snapshot. Rehydration rebuilds
adjacency from the entries and re-derives that hash: a mismatch means some write
landed and some did not, which is reported as ``stale`` and disables expansion. A
collection written before this feature has no graph metadata at all and is ``missing``.
Neither is ever an error — retrieval simply stops expanding.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Sequence, Set, Tuple

GRAPH_SCHEMA_VERSION = 1

# All four must be present together; a subset means a half-written snapshot.
GRAPH_METADATA_KEYS = {
    "graph_schema_version",
    "graph_snapshot_hash",
    "graph_nodes",
    "graph_edges",
}


def encode_outgoing(outgoing: Set[str]) -> str:
    """Canonical on-entry form: compact JSON, ids sorted, so equal graphs compare equal."""
    return json.dumps(sorted(outgoing), separators=(",", ":"))


def decode_outgoing(value: object) -> Tuple[Set[str], bool]:
    """Parse a stored edge list. The flag is False when the record is not canonical."""
    if not isinstance(value, str):
        return set(), False
    try:
        decoded = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return set(), False
    if not isinstance(decoded, list) or not all(isinstance(item, str) for item in decoded):
        return set(), False
    return set(decoded), decoded == sorted(set(decoded))


def snapshot_hash(outgoing: Mapping[str, Set[str]]) -> str:
    """A stable fingerprint of the whole graph, independent of insertion order."""
    canonical = {note_id: sorted(outgoing[note_id]) for note_id in sorted(outgoing)}
    rendered = json.dumps(
        canonical, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def edge_count(outgoing: Mapping[str, Set[str]]) -> int:
    return sum(len(targets) for targets in outgoing.values())


@dataclass
class GraphSnapshot:
    """Adjacency rebuilt from an index, plus whether it can be trusted."""

    outgoing: Dict[str, Set[str]]
    incoming: Dict[str, Set[str]]
    status: str  # "ok" | "missing" | "stale"
    schema_version: Optional[int]

    def neighbors(self, note_id: str) -> Set[str]:
        """Symmetric one-hop neighbours; empty unless the snapshot is trustworthy."""
        if self.status != "ok":
            return set()
        return set(self.outgoing.get(note_id, set())) | set(
            self.incoming.get(note_id, set())
        )

    def degree(self, note_id: str) -> int:
        return len(self.neighbors(note_id))

    def report(self) -> Dict[str, object]:
        """The four fields `sync` and `stats` publish."""
        return {
            "graph_status": self.status,
            "graph_nodes": len(self.outgoing),
            "graph_edges": edge_count(self.outgoing),
            "graph_schema_version": self.schema_version,
        }


def resolve(
    document_metadatas: Sequence[Mapping[str, object]],
    collection_metadata: Optional[Mapping[str, object]],
) -> GraphSnapshot:
    """Rebuild adjacency from document entries and judge it against the stored hash."""
    outgoing: Dict[str, Set[str]] = {}
    canonical = True
    for metadata in document_metadatas:
        note_id = str(metadata.get("note_id", ""))
        if not note_id or note_id in outgoing:
            # A missing or duplicated note id means the entries are not the shape
            # sync writes; refuse to call the result healthy.
            canonical = False
            continue
        targets, well_formed = decode_outgoing(metadata.get("graph_outgoing"))
        outgoing[note_id] = targets
        canonical = canonical and well_formed

    known = set(outgoing)
    for note_id, targets in outgoing.items():
        resolved = (targets & known) - {note_id}
        if resolved != targets:
            # Dangling or self-referential edges never survive a real sync.
            canonical = False
        outgoing[note_id] = resolved

    incoming: Dict[str, Set[str]] = {note_id: set() for note_id in outgoing}
    for source, targets in outgoing.items():
        for target in targets:
            incoming[target].add(source)

    metadata = dict(collection_metadata or {})
    stored_version = metadata.get("graph_schema_version")
    version = (
        stored_version
        if isinstance(stored_version, int) and not isinstance(stored_version, bool)
        else None
    )

    present = GRAPH_METADATA_KEYS.intersection(metadata)
    if not present:
        return GraphSnapshot(outgoing, incoming, "missing", version)

    healthy = (
        present == GRAPH_METADATA_KEYS
        and canonical
        and version == GRAPH_SCHEMA_VERSION
        and metadata.get("graph_snapshot_hash") == snapshot_hash(outgoing)
        and metadata.get("graph_nodes") == len(outgoing)
        and metadata.get("graph_edges") == edge_count(outgoing)
    )
    return GraphSnapshot(outgoing, incoming, "ok" if healthy else "stale", version)
