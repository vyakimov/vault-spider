"""Read-only corpus health report (no LLM, no writes, no Chroma dependency)."""

from __future__ import annotations

import difflib
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vault_spider import settings
from vault_spider.corpus.frontmatter import coerce_datetime, normalize_tags, split_frontmatter
from vault_spider.corpus.links import INLINE_CODE_RE, WIKILINK_RE, build_link_graph
from vault_spider.corpus.loader import (
    has_ignore_frontmatter_tag,
    has_ignore_tag,
    is_excalidraw,
)
from vault_spider.corpus.vault import (
    VaultNote,
    iter_attachment_files,
    iter_note_files,
    load_vault_notes,
)

TIMESTAMP_FIELDS = ("created", "updated", "date")
CONTRACT_FIELDS = ("id", "created", "updated")

# A body this short carries no retrievable content; such a note is a stub.
EMPTY_NOTE_MAX_CHARS = 20
# Obsidian sync writes conflict copies as "Note 1.md" alongside "Note.md".
CONFLICT_COPY_RE = re.compile(r"^(?P<base>.+) \d+$")


def _timestamp_problem(value: Any) -> Optional[str]:
    if coerce_datetime(value) is None:
        return "unparseable"
    has_offset = False
    if isinstance(value, datetime):
        has_offset = value.tzinfo is not None
    elif isinstance(value, date):
        has_offset = False
    elif isinstance(value, str):
        stripped = value.strip()
        has_offset = stripped.endswith("Z") or bool(
            re.search(r"[+-]\d{2}:?\d{2}$", stripped)
        )

    if settings.timestamp_policy() == "obsidian_local":
        return "offset_aware" if has_offset else None
    return None if has_offset else "naive"


def _note_recency(frontmatter: Dict[str, Any]) -> Optional[datetime]:
    for key in ("updated", "date", "created"):
        resolved = coerce_datetime(frontmatter.get(key))
        if resolved is not None:
            return resolved
    return None


def _sources_wikilinks(body: str) -> List[Tuple[str, int]]:
    """Wikilinks under a `## Sources` heading (until the next heading or EOF)."""
    lines = body.split("\n")
    in_fence = False
    collecting = False
    collected: List[Tuple[str, int]] = []
    for index, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            if collecting:
                break
            if heading.group(2).strip().lower() == "sources":
                collecting = True
            continue
        if collecting:
            cleaned = INLINE_CODE_RE.sub("", line)
            for match in WIKILINK_RE.finditer(cleaned):
                collected.append((match.group(1).strip(), index))
    return collected


def lint_vault(root: str) -> Dict[str, Any]:
    root_path = Path(root)
    notes, notes_ignored = load_vault_notes(root)

    notes_by_path = {note.path: note for note in notes}
    graph = build_link_graph(notes, iter_attachment_files(root_path))
    resolver = graph.resolver
    outgoing, incoming = graph.outgoing, graph.incoming

    findings: Dict[str, List[Dict[str, Any]]] = {
        "missing_frontmatter_fields": [],
        "invalid_timestamps": [],
        "duplicate_ids": [],
        "duplicate_titles": [],
        "broken_wikilinks": [],
        "dangling_targets": [],
        "empty_notes": [],
        "conflict_copies": [],
        "orphans": [],
        "stale_distilled": [],
        "imported_missing_source": [],
    }

    # missing_frontmatter_fields
    for note in notes:
        missing = [f for f in CONTRACT_FIELDS if f not in note.frontmatter]
        if missing:
            findings["missing_frontmatter_fields"].append({"path": note.path, "missing": missing})

    # invalid_timestamps
    for note in notes:
        for field_name in TIMESTAMP_FIELDS:
            if field_name not in note.frontmatter:
                continue
            problem = _timestamp_problem(note.frontmatter[field_name])
            if problem:
                findings["invalid_timestamps"].append(
                    {
                        "path": note.path,
                        "field": field_name,
                        "value": str(note.frontmatter[field_name]),
                        "problem": problem,
                    }
                )

    # duplicate_ids
    ids: Dict[str, List[str]] = {}
    for note in notes:
        raw_id = note.frontmatter.get("id")
        if raw_id is None:
            continue
        ids.setdefault(str(raw_id).strip(), []).append(note.path)
    for note_id, paths in ids.items():
        if len(paths) >= 2:
            findings["duplicate_ids"].append({"id": note_id, "paths": sorted(paths)})

    # duplicate_titles
    titles: Dict[str, List[VaultNote]] = {}
    for note in notes:
        titles.setdefault(note.title.lower(), []).append(note)
    for title_notes in titles.values():
        if len(title_notes) >= 2:
            findings["duplicate_titles"].append(
                {
                    "title": title_notes[0].title,
                    "paths": sorted(note.path for note in title_notes),
                }
            )
    findings["duplicate_titles"].sort(key=lambda finding: str(finding["title"]).lower())

    # broken_wikilinks — every target the graph could resolve to neither a note nor an
    # attachment, in vault order (body links before frontmatter links, per note).
    findings["broken_wikilinks"] = [
        {"path": link.path, "target": link.target, "line": link.line, "location": link.location}
        for link in graph.unresolved
    ]

    # dangling_targets — unresolved targets aggregated by how often they are linked.
    # The most-linked missing note is the most valuable one to write next.
    dangling: Dict[str, List[str]] = {}
    for finding in findings["broken_wikilinks"]:
        dangling.setdefault(str(finding["target"]), []).append(str(finding["path"]))
    findings["dangling_targets"] = sorted(
        (
            {"target": target, "count": len(paths), "linked_from": sorted(set(paths))}
            for target, paths in dangling.items()
        ),
        key=lambda entry: (-int(entry["count"]), str(entry["target"]).lower()),
    )

    # empty_notes — a stub with inbound links is the highest-value note to fill in.
    for note in notes:
        chars = len(note.body.strip())
        if chars <= EMPTY_NOTE_MAX_CHARS:
            findings["empty_notes"].append(
                {"path": note.path, "chars": chars, "inbound": len(incoming[note.path])}
            )
    findings["empty_notes"].sort(
        key=lambda entry: (-int(entry["inbound"]), str(entry["path"]))
    )

    # conflict_copies — Obsidian sync writes "Note 1.md" next to "Note.md".
    for note in notes:
        match = CONFLICT_COPY_RE.match(note.stem)
        if match is None:
            continue
        base_path = (Path(note.path).parent / f"{match.group('base')}.md").as_posix()
        base = notes_by_path.get(base_path)
        if base is None:
            continue
        similarity = difflib.SequenceMatcher(
            None, base.body.strip(), note.body.strip()
        ).ratio()
        findings["conflict_copies"].append(
            {
                "path": note.path,
                "base_path": base.path,
                "similarity": round(similarity, 3),
            }
        )
    # imported_missing_source: reference/llm notes should carry source_url
    for note in notes:
        if note.provenance in ("reference", "llm") and not str(
            note.frontmatter.get("source_url") or ""
        ).strip():
            findings["imported_missing_source"].append(
                {"path": note.path, "provenance": note.provenance}
            )

    findings["conflict_copies"].sort(key=lambda entry: -float(entry["similarity"]))

    # orphans (distilled notes excluded — their Sources always link out)
    for note in notes:
        if note.provenance == "distilled" or note.note_type == "distilled":
            continue
        if not outgoing[note.path] and not incoming[note.path]:
            findings["orphans"].append({"path": note.path})

    # stale_distilled
    for note in notes:
        if note.provenance != "distilled" and note.note_type != "distilled":
            continue
        stale_sources = []
        for target, _ in _sources_wikilinks(note.body):
            resolved = resolver.resolve(target)
            if resolved is None:
                findings["stale_distilled"].append(
                    {"path": note.path, "warning": f"unresolvable source link {target}"}
                )
                continue
            source = notes_by_path.get(resolved)
            if source is None or source.recency is None or note.recency is None:
                continue
            if source.recency > note.recency:
                stale_sources.append(
                    {
                        "source_path": source.path,
                        "source_updated": source.recency.isoformat(),
                        "distilled_updated": note.recency.isoformat(),
                    }
                )
        if stale_sources:
            findings["stale_distilled"].append(
                {"path": note.path, "stale_sources": stale_sources}
            )

    summary = {key: len(value) for key, value in findings.items()}
    return {
        "root": str(root),
        "notes_scanned": len(notes),
        "notes_ignored": notes_ignored,
        "summary": summary,
        "findings": findings,
    }


def _rewrite_frontmatter_field(raw: str, field_name: str, value: str) -> Optional[str]:
    """Replace a top-level frontmatter field's value, leaving the rest byte-identical."""
    if not raw.startswith("---\n"):
        return None
    lines = raw.split("\n")
    pattern = re.compile(rf"^{re.escape(field_name)}\s*:", re.IGNORECASE)
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return None  # hit the closing fence without finding the field
        if pattern.match(lines[index]):
            lines[index] = f"{field_name}: {value}"
            return "\n".join(lines)
    return None


def fix_naive_timestamps(root: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Normalize `created`/`updated`/`date` to the configured timestamp policy.

    For the aware policies this attaches an offset to naive local wall-clock values.
    For ``obsidian_local`` it converts aware instants to local wall time and removes the
    suffix so Obsidian can render them as native Date & time properties. Unparseable
    values are never guessed at; they are skipped and reported.
    """
    from vault_spider.compounding.backfill_core import format_timestamp

    root_path = Path(root)
    fixed: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for path, rel in iter_note_files(root_path):
        try:
            original_stat = path.stat()
            raw = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        frontmatter, body = split_frontmatter(raw)
        if has_ignore_tag(body) or has_ignore_frontmatter_tag(
            normalize_tags(frontmatter.get("tags"))
        ):
            continue
        if is_excalidraw(Path(rel), frontmatter):
            continue

        updated_raw = raw
        changed: List[Dict[str, str]] = []
        for field_name in TIMESTAMP_FIELDS:
            if field_name not in frontmatter:
                continue
            value = frontmatter[field_name]
            problem = _timestamp_problem(value)
            if problem is None:
                continue
            if problem == "unparseable":
                skipped.append({"path": rel, "field": field_name, "reason": problem})
                continue
            resolved = coerce_datetime(value)
            if resolved is None:  # defensive: policy mismatches imply it parsed
                skipped.append({"path": rel, "field": field_name, "reason": "unparseable"})
                continue
            new_value = format_timestamp(resolved)
            rewritten = _rewrite_frontmatter_field(updated_raw, field_name, new_value)
            if rewritten is None:
                skipped.append(
                    {"path": rel, "field": field_name, "reason": "field not found in frontmatter"}
                )
                continue
            updated_raw = rewritten
            changed.append({"field": field_name, "from": str(value), "to": new_value})

        if changed:
            path.write_text(updated_raw, encoding="utf-8")
            # Formatting-only timestamp migrations must not make a note look newly
            # edited (or provoke a modified-date plugin to stamp the migration time).
            os.utime(path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            fixed.append({"path": rel, "timestamps": changed})

    return fixed, skipped


def fix_missing_frontmatter(root: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    from vault_spider.compounding.backfill_core import (
        _as_str,
        apply_changes_to_text,
        detect_ambiguity,
        git_context,
        resolve_created,
        resolve_id,
        resolve_updated,
    )

    root_path = Path(root)
    initial = lint_vault(root)
    target_paths = {
        finding["path"]
        for finding in initial["findings"]["missing_frontmatter_fields"]
    }
    records = []
    id_counts: Dict[str, int] = {}
    for path, rel in iter_note_files(root_path):
        try:
            raw = path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        frontmatter, body = split_frontmatter(raw)
        if has_ignore_tag(body) or has_ignore_frontmatter_tag(
            normalize_tags(frontmatter.get("tags"))
        ):
            continue
        records.append((path, rel, raw, frontmatter))
        if "id" in frontmatter:
            note_id = str(frontmatter["id"]).strip()
            id_counts[note_id] = id_counts.get(note_id, 0) + 1

    git = git_context(root_path)
    fixed: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    for path, rel, raw, frontmatter in records:
        if rel not in target_paths:
            continue
        ambiguity = detect_ambiguity(frontmatter, raw, id_counts)
        if ambiguity is not None:
            skipped.append({"path": rel, "reason": ambiguity[0]})
            continue
        stat = path.stat()
        changes = [
            change
            for change in (
                resolve_id(frontmatter),
                resolve_created(frontmatter, root_path, rel, git, stat),
                resolve_updated(frontmatter, root_path, rel, git, stat),
            )
            if change is not None
        ]
        by_field = {change.field: change for change in changes}
        created_value = (
            by_field["created"].value
            if "created" in by_field
            else frontmatter.get("created")
        )
        if "updated" in by_field and created_value:
            updated_dt = coerce_datetime(by_field["updated"].value)
            created_dt = coerce_datetime(created_value)
            if updated_dt is not None and created_dt is not None and updated_dt < created_dt:
                by_field["updated"].value = _as_str(created_value)
                by_field["updated"].warnings.append(
                    "updated predated created; clamped to created"
                )
        path.write_text(apply_changes_to_text(raw, changes), encoding="utf-8")
        fixed.append({"path": rel, "fields": [change.field for change in changes]})
    return fixed, skipped
