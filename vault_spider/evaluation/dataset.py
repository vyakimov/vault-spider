"""Load and validate a golden evaluation dataset (manifest, queries, corpus labels).

A dataset is a directory holding a ``dataset.yaml`` manifest, a JSONL golden-query
file, and a corpus of Markdown notes. Paths, note ids, and headings in the golden
set are stable evaluation identifiers; ``validate()`` cross-checks every label
against the corpus exactly as sync would see it (same skip/ignore rules), so a
renamed heading or moved note fails validation instead of silently zeroing scores.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from vault_spider.corpus.chunker import split_sections
from vault_spider.corpus.loader import load_notes

EVAL_SCHEMA_VERSION = 1

_MANIFEST_REQUIRED = ("eval_schema_version", "name", "corpus_root", "queries_file")
_MANIFEST_KNOWN = set(_MANIFEST_REQUIRED) | {
    "description",
    "expected_note_count",
    "expected_query_count",
    "privacy",
    "timestamp_policy",
    "license_note",
}
_QUERY_REQUIRED = (
    "id",
    "query",
    "answerable",
    "category",
    "slices",
    "relevant_evidence",
    "required_evidence_groups",
    "gold_facts",
    "forbidden_facts",
)
_EVIDENCE_REQUIRED = ("note_id", "path", "heading", "grade")
_FILTER_KEYS = {"type", "folder", "tags", "since", "until"}
# Evidence grades: 3 answers directly, 2 is required support, 1 related, 0 hard negative.
_GRADES = (0, 1, 2, 3)
# Every required_evidence_groups member must be labeled required support or better.
_GROUP_MIN_GRADE = 2


class DatasetError(ValueError):
    """The dataset cannot be loaded at all (missing or unparseable files)."""


class DatasetNotFoundError(DatasetError):
    """The --dataset path (or its dataset.yaml) does not exist."""


@dataclass
class EvalDataset:
    path: Path                     # the dataset.yaml manifest
    manifest: Dict[str, Any]
    corpus_root: Path
    queries: List[Dict[str, Any]]  # parsed JSONL rows, in file order

    @property
    def name(self) -> str:
        return str(self.manifest.get("name") or self.path.parent.name)


@dataclass
class ValidationReport:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.errors


def load_dataset(dataset_arg: str) -> EvalDataset:
    """Parse the manifest and query file strictly; semantic checks live in validate()."""
    path = Path(dataset_arg).expanduser()
    if path.is_dir():
        path = path / "dataset.yaml"
    if not path.is_file():
        raise DatasetNotFoundError(f"dataset manifest not found: {path}")
    path = path.resolve()

    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise DatasetError(f"{path} is not valid YAML: {exc}") from exc
    if not isinstance(manifest, dict):
        raise DatasetError(f"{path} must be a YAML mapping")
    missing = [key for key in _MANIFEST_REQUIRED if key not in manifest]
    if missing:
        raise DatasetError(f"{path} is missing manifest key(s): {', '.join(missing)}")
    version = manifest["eval_schema_version"]
    if version != EVAL_SCHEMA_VERSION:
        raise DatasetError(
            f"unsupported eval_schema_version {version!r} (supported: {EVAL_SCHEMA_VERSION})"
        )

    corpus_root = (path.parent / str(manifest["corpus_root"])).resolve()
    if not corpus_root.is_dir():
        raise DatasetError(f"corpus_root directory not found: {corpus_root}")
    queries_path = (path.parent / str(manifest["queries_file"])).resolve()
    if not queries_path.is_file():
        raise DatasetError(f"queries_file not found: {queries_path}")

    queries: List[Dict[str, Any]] = []
    with queries_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{queries_path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise DatasetError(f"{queries_path}:{line_no}: query must be a JSON object")
            queries.append(row)
    if not queries:
        raise DatasetError(f"{queries_path} contains no queries")

    return EvalDataset(path=path, manifest=manifest, corpus_root=corpus_root, queries=queries)


@dataclass
class CorpusNote:
    note_id: str
    headings: Set[str]  # section headings retrieval can address (H1-H3; "" = preamble)


def corpus_labels(corpus_root: Path) -> Dict[str, CorpusNote]:
    """Corpus notes exactly as sync sees them, keyed by vault-relative path.

    A note whose body has no H1-H3 headings yields one preamble section with
    heading "" — labels may target it with an empty heading string.
    """
    return {
        note.path: CorpusNote(
            note_id=note.note_id,
            headings={section.heading for section in split_sections(note)},
        )
        for note in load_notes(str(corpus_root))
    }


def _is_str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _shape_errors(label: str, row: Dict[str, Any]) -> List[str]:
    """Type-level problems with one query row; empty means the row is well-formed."""
    errors: List[str] = []
    for key in ("id", "query", "category"):
        if not isinstance(row[key], str) or not row[key].strip():
            errors.append(f"{label}: {key} must be a non-empty string")
    if not isinstance(row["answerable"], bool):
        errors.append(f"{label}: answerable must be a boolean")
    for key in ("slices", "gold_facts", "forbidden_facts"):
        if not _is_str_list(row[key]):
            errors.append(f"{label}: {key} must be an array of strings")

    evidence = row["relevant_evidence"]
    if not isinstance(evidence, list):
        errors.append(f"{label}: relevant_evidence must be an array")
    else:
        for index, entry in enumerate(evidence):
            where = f"{label}: relevant_evidence[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{where} must be an object")
                continue
            missing = [key for key in _EVIDENCE_REQUIRED if key not in entry]
            if missing:
                errors.append(f"{where} is missing {', '.join(missing)}")
                continue
            for key in ("note_id", "path"):
                if not isinstance(entry[key], str) or not entry[key].strip():
                    errors.append(f"{where}: {key} must be a non-empty string")
            # "" is a valid heading: it addresses a heading-less note's preamble.
            if not isinstance(entry["heading"], str):
                errors.append(f"{where}: heading must be a string")
            grade = entry["grade"]
            if isinstance(grade, bool) or grade not in _GRADES:
                errors.append(f"{where}: grade must be an integer 0-3")

    groups = row["required_evidence_groups"]
    if not isinstance(groups, list):
        errors.append(f"{label}: required_evidence_groups must be an array")
    else:
        for index, group in enumerate(groups):
            where = f"{label}: required_evidence_groups[{index}]"
            if not _is_str_list(group) or not group:
                errors.append(f"{where} must be a non-empty array of strings")
                continue
            for ref in group:
                if "#" not in ref:
                    errors.append(f"{where}: member {ref!r} must be '<note_id>#<heading>'")

    filters = row.get("filters")
    if filters is not None:
        if not isinstance(filters, dict):
            errors.append(f"{label}: filters must be an object")
        else:
            unknown = sorted(set(filters) - _FILTER_KEYS)
            if unknown:
                errors.append(
                    f"{label}: unknown filter key(s): {', '.join(unknown)} "
                    f"(known: {', '.join(sorted(_FILTER_KEYS))})"
                )
            tags = filters.get("tags")
            if tags is not None and not _is_str_list(tags):
                errors.append(f"{label}: filters.tags must be an array of strings")
            for key in _FILTER_KEYS - {"tags"}:
                if key in filters and not isinstance(filters[key], str):
                    errors.append(f"{label}: filters.{key} must be a string")
    return errors


def validate(dataset: EvalDataset) -> ValidationReport:
    """Semantic validation: labels resolve, contracts hold, counts match."""
    report = ValidationReport()
    errors, warnings = report.errors, report.warnings

    corpus = corpus_labels(dataset.corpus_root)
    if not corpus:
        errors.append(f"corpus: no notes found under {dataset.corpus_root}")
    id_to_path: Dict[str, str] = {}
    for path, note in corpus.items():
        if note.note_id in id_to_path:
            errors.append(
                f"corpus: duplicate note id {note.note_id} "
                f"({id_to_path[note.note_id]} and {path})"
            )
        id_to_path[note.note_id] = path

    unknown_keys = sorted(set(dataset.manifest) - _MANIFEST_KNOWN)
    if unknown_keys:
        warnings.append(f"manifest: unknown key(s): {', '.join(unknown_keys)}")
    expected_notes = dataset.manifest.get("expected_note_count")
    if expected_notes is not None and expected_notes != len(corpus):
        errors.append(
            f"manifest: expected_note_count is {expected_notes} "
            f"but the corpus has {len(corpus)} notes"
        )
    expected_queries = dataset.manifest.get("expected_query_count")
    if expected_queries is not None and expected_queries != len(dataset.queries):
        errors.append(
            f"manifest: expected_query_count is {expected_queries} "
            f"but the file has {len(dataset.queries)} queries"
        )

    seen_ids: Set[str] = set()
    referenced_paths: Set[str] = set()
    answerable_count = 0
    unanswerable_count = 0
    categories: Dict[str, int] = {}

    for index, row in enumerate(dataset.queries, start=1):
        raw_id = row.get("id")
        label = raw_id if isinstance(raw_id, str) and raw_id else f"query line {index}"
        missing = [key for key in _QUERY_REQUIRED if key not in row]
        if missing:
            errors.append(f"{label}: missing field(s): {', '.join(missing)}")
            continue
        shape = _shape_errors(label, row)
        if shape:
            errors.extend(shape)
            continue

        if row["id"] in seen_ids:
            errors.append(f"{label}: duplicate query id")
        seen_ids.add(row["id"])
        categories[row["category"]] = categories.get(row["category"], 0) + 1

        evidence = row["relevant_evidence"]
        groups = row["required_evidence_groups"]
        if row["answerable"]:
            answerable_count += 1
            if not any(entry["grade"] == 3 for entry in evidence):
                errors.append(f"{label}: answerable but has no grade-3 evidence")
            if not groups:
                errors.append(f"{label}: answerable but required_evidence_groups is empty")
            if not row["gold_facts"]:
                errors.append(f"{label}: answerable but gold_facts is empty")
        else:
            unanswerable_count += 1
            if evidence or groups or row["gold_facts"]:
                errors.append(
                    f"{label}: unanswerable queries must have empty relevant_evidence, "
                    "required_evidence_groups, and gold_facts"
                )

        evidence_grades: Dict[str, int] = {}
        for entry in evidence:
            ref = f"{entry['note_id']}#{entry['heading']}"
            if ref in evidence_grades:
                warnings.append(f"{label}: duplicate evidence entry {ref}")
            evidence_grades[ref] = max(evidence_grades.get(ref, 0), entry["grade"])
            note = corpus.get(entry["path"])
            if note is None:
                errors.append(f"{label}: evidence path not in corpus: {entry['path']}")
                continue
            referenced_paths.add(entry["path"])
            if note.note_id != entry["note_id"]:
                errors.append(
                    f"{label}: evidence note_id {entry['note_id']} does not match "
                    f"{entry['path']} (actual id {note.note_id})"
                )
            if entry["heading"] not in note.headings:
                errors.append(
                    f"{label}: heading {entry['heading']!r} is not a retrievable "
                    f"section of {entry['path']} (H1-H3 headings, or '' for the "
                    "preamble of a heading-less note)"
                )

        for group in groups:
            for ref in group:
                grade = evidence_grades.get(ref)
                if grade is None:
                    errors.append(
                        f"{label}: group member {ref} is not listed in relevant_evidence"
                    )
                elif grade < _GROUP_MIN_GRADE:
                    errors.append(
                        f"{label}: group member {ref} has grade {grade}; "
                        f"required evidence needs grade >= {_GROUP_MIN_GRADE}"
                    )

    report.stats = {
        "notes": len(corpus),
        "queries": len(dataset.queries),
        "answerable": answerable_count,
        "unanswerable": unanswerable_count,
        "labeled_notes": len(referenced_paths),
        "distractor_notes": len(corpus) - len(referenced_paths),
        "categories": dict(sorted(categories.items())),
    }
    return report
