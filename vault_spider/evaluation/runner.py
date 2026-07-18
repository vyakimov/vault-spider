"""Execute a validated golden dataset against the index and score the results.

The retrieval stage is fully deterministic given the index: graded labels are
matched against ranked candidates by (path, heading). The optional synthesis
stage adds abstention scoring plus an LLM judge for gold/forbidden facts, so
its fact metrics inherit the judge model's variance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import log2
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from vault_spider.corpus.loader import load_notes
from vault_spider.envelope import CliError
from vault_spider.evaluation.dataset import EvalDataset
from vault_spider.retrieval.evidence import build_retrieval_output
from vault_spider.synthesis.answer import parse_llm_json, synthesize

RESULTS_SCHEMA_VERSION = 1

_JUDGE_SYSTEM_PROMPT = """You are a strict evaluation judge.
You are given an ANSWER and a numbered list of STATEMENTS.
For each statement, decide whether the answer asserts or presupposes it.
Judge only what the answer says; do not use outside knowledge, and do not
judge whether the statement is true — only whether the answer claims it.
Return JSON with this exact shape: {"verdicts": [true, false, ...]}
The array must contain exactly one boolean per statement, in the given order.
"""

# A label unit is (path, heading); note-level scoring collapses heading to "".
Unit = Tuple[str, str]


def _is_document(candidate: Dict[str, Any]) -> bool:
    return str(candidate.get("chunk_id", "")).endswith("::doc")


def _matches(candidate: Dict[str, Any], unit: Unit, note_level: bool) -> bool:
    """A candidate covers a label if it is that section or contains the whole note."""
    path, heading = unit
    if candidate.get("path") != path:
        return False
    if note_level or _is_document(candidate):
        return True
    return candidate.get("heading") == heading


def _label_units(
    row: Dict[str, Any], note_level: bool
) -> Tuple[Dict[Unit, int], Dict[str, Unit]]:
    """Graded label units plus the group-ref -> unit mapping for one query."""
    grades: Dict[Unit, int] = {}
    ref_units: Dict[str, Unit] = {}
    for entry in row["relevant_evidence"]:
        unit = (entry["path"], "" if note_level else entry["heading"])
        grades[unit] = max(grades.get(unit, 0), int(entry["grade"]))
        ref_units[f"{entry['note_id']}#{entry['heading']}"] = unit
    return grades, ref_units


def score_retrieval(
    row: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    k: int,
    note_level: bool = False,
) -> Dict[str, Any]:
    grades, ref_units = _label_units(row, note_level)
    positive = {unit: grade for unit, grade in grades.items() if grade > 0}

    # nDCG@k: each labeled unit counts once, at the first candidate covering it.
    # A candidate covering several unclaimed units (a whole-note match) claims
    # the highest-graded one.
    claimed: Set[Unit] = set()
    dcg = 0.0
    matched: List[Dict[str, Any]] = []
    for rank, candidate in enumerate(candidates[:k], start=1):
        best: Optional[Unit] = None
        for unit, grade in positive.items():
            if unit in claimed or not _matches(candidate, unit, note_level):
                continue
            if best is None or grade > positive[best]:
                best = unit
        if best is None:
            continue
        claimed.add(best)
        dcg += positive[best] / log2(rank + 1)
        matched.append(
            {"rank": rank, "path": best[0], "heading": best[1], "grade": positive[best]}
        )
    ideal = sorted(positive.values(), reverse=True)[:k]
    idcg = sum(grade / log2(rank + 1) for rank, grade in enumerate(ideal, start=1))
    ndcg = dcg / idcg if idcg else 0.0

    # Required-evidence groups: any member satisfies its group; all groups must
    # be covered inside the top k for the retrieval to count as complete.
    satisfied = 0
    unsatisfied: List[List[str]] = []
    for group in row["required_evidence_groups"]:
        units = [ref_units[ref] for ref in group if ref in ref_units]
        hit = any(
            _matches(candidate, unit, note_level)
            for candidate in candidates[:k]
            for unit in units
        )
        if hit:
            satisfied += 1
        else:
            unsatisfied.append(list(group))
    total_groups = len(row["required_evidence_groups"])
    group_recall = satisfied / total_groups if total_groups else 0.0

    # Reciprocal rank of the first direct answer (grade 3), over all candidates.
    grade3 = {unit for unit, grade in positive.items() if grade == 3}
    first_rank: Optional[int] = None
    for rank, candidate in enumerate(candidates, start=1):
        if any(_matches(candidate, unit, note_level) for unit in grade3):
            first_rank = rank
            break

    missed = [
        {"path": unit[0], "heading": unit[1], "grade": grade}
        for unit, grade in sorted(positive.items())
        if unit not in claimed and grade >= 2
    ]
    return {
        "ndcg_at_k": round(ndcg, 4),
        "group_recall_at_k": round(group_recall, 4),
        "complete_at_k": total_groups > 0 and satisfied == total_groups,
        "first_grade3_rank": first_rank,
        "reciprocal_rank": round(1.0 / first_rank, 4) if first_rank else 0.0,
        "matched": matched,
        "missed": missed,
        "unsatisfied_groups": unsatisfied,
    }


def _judge_facts(provider, answer: str, statements: List[str]) -> Optional[List[bool]]:
    numbered = "\n".join(
        f"{index}. {statement}" for index, statement in enumerate(statements, start=1)
    )
    user_prompt = f"<ANSWER>\n{answer}\n</ANSWER>\n<STATEMENTS>\n{numbered}\n</STATEMENTS>"
    raw = provider.chat(_JUDGE_SYSTEM_PROMPT, user_prompt, temperature=0.0)
    parsed = parse_llm_json(raw)
    if not isinstance(parsed, dict):
        return None
    verdicts = parsed.get("verdicts")
    if (
        not isinstance(verdicts, list)
        or len(verdicts) != len(statements)
        or not all(isinstance(verdict, bool) for verdict in verdicts)
    ):
        return None
    return verdicts


def score_synthesis(
    row: Dict[str, Any],
    synth: Dict[str, Any],
    provider,
    note_level: bool = False,
) -> Dict[str, Any]:
    answerable = row["answerable"]
    abstained = bool(synth.get("abstained"))
    entry: Dict[str, Any] = {
        "abstained": abstained,
        "abstention_correct": abstained == (not answerable),
        "confidence": synth.get("confidence"),
        "warnings": list(synth.get("warnings") or []),
    }

    if answerable:
        # Do the model's citations cover every required evidence group?
        _, ref_units = _label_units(row, note_level)
        citations = synth.get("citations") or []
        satisfied = 0
        for group in row["required_evidence_groups"]:
            units = [ref_units[ref] for ref in group if ref in ref_units]
            if any(
                _matches(citation, unit, note_level)
                for citation in citations
                for unit in units
            ):
                satisfied += 1
        total_groups = len(row["required_evidence_groups"])
        entry["citation_group_recall"] = (
            round(satisfied / total_groups, 4) if total_groups else 0.0
        )
        entry["citation_complete"] = total_groups > 0 and satisfied == total_groups

    gold = list(row["gold_facts"]) if answerable else []
    forbidden = list(row["forbidden_facts"])
    answer = synth.get("answer") or ""
    if not abstained and answer and (gold or forbidden):
        verdicts = _judge_facts(provider, answer, gold + forbidden)
        if verdicts is None:
            entry["judge_failed"] = True
        else:
            if gold:
                gold_verdicts = verdicts[: len(gold)]
                entry["gold_facts_present"] = sum(gold_verdicts)
                entry["gold_facts_total"] = len(gold)
                entry["gold_fact_coverage"] = round(sum(gold_verdicts) / len(gold), 4)
                entry["gold_facts_missing"] = [
                    fact for fact, verdict in zip(gold, gold_verdicts) if not verdict
                ]
            if forbidden:
                entry["forbidden_facts_present"] = [
                    fact
                    for fact, verdict in zip(forbidden, verdicts[len(gold):])
                    if verdict
                ]
    return entry


def _mean(values: List[float]) -> Optional[float]:
    return round(sum(values) / len(values), 4) if values else None


def _aggregate_retrieval(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    scored = [entry["retrieval"] for entry in entries if "retrieval" in entry]
    return {
        "queries_scored": len(scored),
        "mean_ndcg_at_k": _mean([score["ndcg_at_k"] for score in scored]),
        "mean_group_recall_at_k": _mean([score["group_recall_at_k"] for score in scored]),
        "complete_rate_at_k": _mean(
            [1.0 if score["complete_at_k"] else 0.0 for score in scored]
        ),
        "mrr": _mean([score["reciprocal_rank"] for score in scored]),
    }


def _aggregate_synthesis(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    scored = [(entry, entry["synthesis"]) for entry in entries if "synthesis" in entry]
    answerable = [score for entry, score in scored if entry["answerable"]]
    unanswerable = [score for entry, score in scored if not entry["answerable"]]
    answered = [score for score in answerable if not score["abstained"]]
    with_forbidden = [
        score
        for _, score in scored
        if "forbidden_facts_present" in score or "judge_failed" in score
    ]
    return {
        "queries_scored": len(scored),
        "abstention_accuracy": _mean(
            [1.0 if score["abstention_correct"] else 0.0 for _, score in scored]
        ),
        "false_abstain_rate": _mean(
            [1.0 if score["abstained"] else 0.0 for score in answerable]
        ),
        "false_answer_rate": _mean(
            [0.0 if score["abstained"] else 1.0 for score in unanswerable]
        ),
        "citation_complete_rate": _mean(
            [1.0 if score.get("citation_complete") else 0.0 for score in answered]
        ),
        "gold_fact_coverage": _mean(
            [
                score["gold_fact_coverage"]
                for score in answerable
                if "gold_fact_coverage" in score
            ]
        ),
        "forbidden_fact_violation_rate": _mean(
            [
                1.0 if score.get("forbidden_facts_present") else 0.0
                for score in with_forbidden
                if "judge_failed" not in score
            ]
        ),
        "judge_failures": sum(
            1 for _, score in scored if score.get("judge_failed")
        ),
    }


def _breakdown(
    entries: List[Dict[str, Any]], keys_of: Callable[[Dict[str, Any]], List[str]]
) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        for key in keys_of(entry):
            grouped.setdefault(key, []).append(entry)
    aggregated = {
        key: _aggregate_retrieval(members) for key, members in sorted(grouped.items())
    }
    return {key: agg for key, agg in aggregated.items() if agg["queries_scored"]}


def run_eval(
    dataset: EvalDataset,
    store,
    provider,
    *,
    stage: str = "retrieval",
    mode: str = "thorough",
    granularity: str = "mixed",
    n: int = 10,
    k: int = 5,
    n_context: int = 8,
    only: Optional[List[str]] = None,
) -> Dict[str, Any]:
    from vault_spider.retrieval.searcher import Searcher

    # The benchmark is only meaningful against an index of exactly this corpus.
    corpus_paths = {note.path for note in load_notes(str(dataset.corpus_root))}
    indexed = store.collection.get(include=["metadatas"])
    indexed_paths = {
        str(metadata.get("path", "")) for metadata in (indexed.get("metadatas") or [])
    }
    if not indexed_paths:
        raise CliError(
            "index_empty",
            "index is empty; run `vault-spider sync --root <corpus>` "
            "against a dedicated --chroma-path first",
        )
    if indexed_paths != corpus_paths:
        raise CliError(
            "config_mismatch",
            "the index does not match the eval corpus; rebuild it with "
            f"`vault-spider sync --root {dataset.corpus_root} --reset` "
            "against a dedicated --chroma-path",
            {
                "missing_from_index": sorted(corpus_paths - indexed_paths)[:10],
                "not_in_corpus": sorted(indexed_paths - corpus_paths)[:10],
            },
        )

    rows = dataset.queries
    if only:
        known = {row["id"] for row in rows}
        unknown = sorted(set(only) - known)
        if unknown:
            raise CliError(
                "invalid_arguments", f"unknown query id(s): {', '.join(unknown)}"
            )
        rows = [row for row in rows if row["id"] in set(only)]

    searcher = Searcher(store, granularity=granularity, provider=provider)
    note_level = granularity == "document"
    entries: List[Dict[str, Any]] = []
    for row in rows:
        entry: Dict[str, Any] = {
            "id": row["id"],
            "category": row["category"],
            "slices": list(row["slices"]),
            "answerable": row["answerable"],
        }
        if not row["answerable"] and stage != "synthesis":
            entry["skipped"] = "unanswerable; abstention is scored with --stage synthesis"
            entries.append(entry)
            continue

        filters = row.get("filters") or {}
        try:
            result = searcher.hybrid_search(
                row["query"],
                mode=mode,
                granularity=granularity,
                n_results=n,
                folder=filters.get("folder"),
                tags=filters.get("tags"),
                note_type=filters.get("type"),
                since=filters.get("since"),
                until=filters.get("until"),
            )
            output = build_retrieval_output(row["query"], mode, granularity, result.rows)
        except ValueError as exc:
            # e.g. filters that match nothing — a real failure for this query,
            # scored as zero rather than aborting the run.
            output = {
                "query": row["query"],
                "mode": mode,
                "granularity": granularity,
                "candidates": [],
            }
            entry["retrieval_error"] = str(exc)

        if row["answerable"]:
            entry["retrieval"] = score_retrieval(
                row, output["candidates"], k, note_level=note_level
            )
        if stage == "synthesis":
            synth = synthesize(
                provider, output, question=row["query"], hard_cutoff=n_context
            )
            entry["synthesis"] = score_synthesis(
                row, synth, provider, note_level=note_level
            )
        entries.append(entry)

    aggregates: Dict[str, Any] = {"retrieval": _aggregate_retrieval(entries)}
    if stage == "synthesis":
        aggregates["synthesis"] = _aggregate_synthesis(entries)

    run_info: Dict[str, Any] = {
        "stage": stage,
        "mode": mode,
        "granularity": granularity,
        "n": n,
        "k": k,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "embedding_model": getattr(provider, "embedding_model", None),
        "rerank_model": getattr(provider, "rerank_model", None),
    }
    if stage == "synthesis":
        run_info["n_context"] = n_context
        run_info["chat_model"] = getattr(provider, "chat_model", None)

    return {
        "results_schema_version": RESULTS_SCHEMA_VERSION,
        "dataset": {
            "name": dataset.name,
            "path": str(dataset.path),
            "eval_schema_version": dataset.manifest["eval_schema_version"],
            "corpus_root": str(dataset.corpus_root),
            "notes": len(corpus_paths),
            "queries": len(rows),
        },
        "run": run_info,
        "aggregates": aggregates,
        "by_category": _breakdown(entries, lambda entry: [entry["category"]]),
        "by_slice": _breakdown(entries, lambda entry: entry["slices"]),
        "queries": entries,
    }
