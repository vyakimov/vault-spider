"""Tests for the eval commands: dataset validation, scoring, and the run loop."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.conftest import FakeProvider
from vault_spider import cli
from vault_spider.evaluation.dataset import (
    DatasetError,
    DatasetNotFoundError,
    load_dataset,
    validate,
)
from vault_spider.evaluation.runner import score_retrieval

REPO_ROOT = Path(__file__).resolve().parent.parent

NOTE_A_ID = "01JEV00000000000000000000A"
NOTE_B_ID = "01JEV00000000000000000000B"
NOTE_C_ID = "01JEV00000000000000000000C"


def run(capsys, argv):
    code = cli.main(argv)
    out = capsys.readouterr().out.strip()
    return code, json.loads(out)


def write_dataset(base: Path) -> Path:
    """A minimal valid dataset: 3 notes, 2 answerable + 1 unanswerable query."""
    dataset_dir = base / "dataset"
    corpus = dataset_dir / "corpus"
    (corpus / "Projects").mkdir(parents=True)
    (corpus / "Ops").mkdir(parents=True)

    (corpus / "Projects" / "Alpha.md").write_text(
        f"---\nid: {NOTE_A_ID}\ntitle: Alpha Gateway\ntype: architecture\n"
        "created: 2024-01-01T10:00:00Z\nupdated: 2024-06-01T10:00:00Z\ntags: [alpha]\n---\n"
        "# Alpha Gateway\n\n"
        "## Buffering\nThe alpha gateway buffers zebra readings in a local queue "
        "for 72 hours.\n\n"
        "## Security\nOnly outbound zebra connections are allowed.\n",
        encoding="utf-8",
    )
    (corpus / "Ops" / "Beta Runbook.md").write_text(
        f"---\nid: {NOTE_B_ID}\ntitle: Beta Runbook\ntype: runbook\n"
        "created: 2024-02-01T10:00:00Z\nupdated: 2024-06-01T10:00:00Z\ntags: [ops]\n---\n"
        "# Beta Runbook\n\n"
        "## Thresholds\nDisk warning fires at 80 percent for the quokka service.\n",
        encoding="utf-8",
    )
    (corpus / "Projects" / "Gamma.md").write_text(
        f"---\nid: {NOTE_C_ID}\ntitle: Gamma Distractor\ntype: note\n"
        "created: 2024-03-01T10:00:00Z\nupdated: 2024-06-01T10:00:00Z\ntags: [misc]\n---\n"
        "# Gamma Distractor\n\n## Trivia\nNothing relevant lives here.\n",
        encoding="utf-8",
    )

    queries = [
        {
            "id": "q1",
            "query": "How long does the alpha gateway buffer readings?",
            "answerable": True,
            "category": "known_item",
            "slices": ["single_note"],
            "relevant_evidence": [
                {
                    "note_id": NOTE_A_ID,
                    "path": "Projects/Alpha.md",
                    "heading": "Buffering",
                    "grade": 3,
                }
            ],
            "required_evidence_groups": [[f"{NOTE_A_ID}#Buffering"]],
            "gold_facts": ["The buffer holds 72 hours of readings."],
            "forbidden_facts": ["The buffer holds 7 hours of readings."],
        },
        {
            "id": "q2",
            "query": "Where are the disk thresholds defined?",
            "answerable": True,
            "category": "metadata_filter",
            "slices": ["type_filter"],
            "filters": {"type": "runbook"},
            "relevant_evidence": [
                {
                    "note_id": NOTE_B_ID,
                    "path": "Ops/Beta Runbook.md",
                    "heading": "Thresholds",
                    "grade": 3,
                }
            ],
            "required_evidence_groups": [[f"{NOTE_B_ID}#Thresholds"]],
            "gold_facts": ["The warning threshold is 80 percent."],
            "forbidden_facts": [],
        },
        {
            "id": "q3",
            "query": "What is the administrator password?",
            "answerable": False,
            "category": "unanswerable",
            "slices": ["abstention"],
            "relevant_evidence": [],
            "required_evidence_groups": [],
            "gold_facts": [],
            "forbidden_facts": [],
        },
    ]
    (dataset_dir / "golden.jsonl").write_text(
        "\n".join(json.dumps(query) for query in queries) + "\n", encoding="utf-8"
    )
    (dataset_dir / "dataset.yaml").write_text(
        "eval_schema_version: 1\n"
        "name: test-eval\n"
        "corpus_root: corpus\n"
        "queries_file: golden.jsonl\n"
        "expected_note_count: 3\n"
        "expected_query_count: 3\n",
        encoding="utf-8",
    )
    return dataset_dir


def rewrite_query(dataset_dir: Path, query_id: str, **changes) -> None:
    path = dataset_dir / "golden.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for row in rows:
        if row["id"] == query_id:
            row.update(changes)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


class TestValidate:
    def test_shipped_dataset_is_valid(self):
        dataset = load_dataset(str(REPO_ROOT / "eval"))
        report = validate(dataset)
        assert report.errors == []
        assert report.stats["notes"] == 36
        assert report.stats["queries"] == 30

    def test_realistic_dataset_is_valid(self):
        dataset_dir = REPO_ROOT / "eval-realistic"
        if not dataset_dir.exists():
            pytest.skip("eval-realistic corpus not present")
        report = validate(load_dataset(str(dataset_dir)))
        assert report.errors == []
        assert report.stats["notes"] == 57
        assert report.stats["queries"] == 30

    def test_valid_dataset_passes(self, tmp_path):
        report = validate(load_dataset(str(write_dataset(tmp_path))))
        assert report.valid
        assert report.stats == {
            "notes": 3,
            "queries": 3,
            "answerable": 2,
            "unanswerable": 1,
            "labeled_notes": 2,
            "distractor_notes": 1,
            "categories": {"known_item": 1, "metadata_filter": 1, "unanswerable": 1},
        }

    def test_preamble_label_on_headingless_note(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        (dataset_dir / "corpus" / "Ops" / "Stub.md").write_text(
            "---\nid: 01JEV00000000000000000000D\ntitle: Stub\n---\n"
            "A body with no headings that answers the quokka retry question.\n",
            encoding="utf-8",
        )
        manifest = dataset_dir / "dataset.yaml"
        manifest.write_text(
            manifest.read_text().replace("expected_note_count: 3", "expected_note_count: 4")
        )
        rewrite_query(
            dataset_dir,
            "q2",
            relevant_evidence=[
                {
                    "note_id": "01JEV00000000000000000000D",
                    "path": "Ops/Stub.md",
                    "heading": "",
                    "grade": 3,
                }
            ],
            required_evidence_groups=[["01JEV00000000000000000000D#"]],
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert report.errors == []

    def test_missing_dataset_raises_not_found(self, tmp_path):
        with pytest.raises(DatasetNotFoundError):
            load_dataset(str(tmp_path / "nowhere"))

    def test_unsupported_schema_version(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        manifest = dataset_dir / "dataset.yaml"
        manifest.write_text(
            manifest.read_text().replace("eval_schema_version: 1", "eval_schema_version: 9")
        )
        with pytest.raises(DatasetError, match="unsupported eval_schema_version"):
            load_dataset(str(dataset_dir))

    def test_heading_typo_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(
            dataset_dir,
            "q1",
            relevant_evidence=[
                {
                    "note_id": NOTE_A_ID,
                    "path": "Projects/Alpha.md",
                    "heading": "Bufferings",
                    "grade": 3,
                }
            ],
            required_evidence_groups=[[f"{NOTE_A_ID}#Bufferings"]],
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("q1" in error and "Bufferings" in error for error in report.errors)

    def test_note_id_mismatch_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(
            dataset_dir,
            "q1",
            relevant_evidence=[
                {
                    "note_id": NOTE_C_ID,
                    "path": "Projects/Alpha.md",
                    "heading": "Buffering",
                    "grade": 3,
                }
            ],
            required_evidence_groups=[[f"{NOTE_C_ID}#Buffering"]],
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("does not match" in error for error in report.errors)

    def test_unanswerable_with_gold_facts_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(dataset_dir, "q3", gold_facts=["Sneaky fact."])
        report = validate(load_dataset(str(dataset_dir)))
        assert any("q3" in error and "unanswerable" in error for error in report.errors)

    def test_group_ref_not_in_evidence_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(
            dataset_dir, "q1", required_evidence_groups=[[f"{NOTE_B_ID}#Thresholds"]]
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("not listed in relevant_evidence" in error for error in report.errors)

    def test_group_ref_low_grade_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(
            dataset_dir,
            "q1",
            relevant_evidence=[
                {
                    "note_id": NOTE_A_ID,
                    "path": "Projects/Alpha.md",
                    "heading": "Buffering",
                    "grade": 3,
                },
                {
                    "note_id": NOTE_A_ID,
                    "path": "Projects/Alpha.md",
                    "heading": "Security",
                    "grade": 1,
                },
            ],
            required_evidence_groups=[[f"{NOTE_A_ID}#Security"]],
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("grade 1" in error for error in report.errors)

    def test_expected_count_mismatch_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        manifest = dataset_dir / "dataset.yaml"
        manifest.write_text(
            manifest.read_text().replace("expected_note_count: 3", "expected_note_count: 4")
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("expected_note_count" in error for error in report.errors)

    def test_duplicate_query_id_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        path = dataset_dir / "golden.jsonl"
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
        manifest = dataset_dir / "dataset.yaml"
        manifest.write_text(
            manifest.read_text().replace("expected_query_count: 3", "expected_query_count: 4")
        )
        report = validate(load_dataset(str(dataset_dir)))
        assert any("duplicate query id" in error for error in report.errors)

    def test_unknown_filter_key_is_error(self, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        rewrite_query(dataset_dir, "q2", filters={"kind": "runbook"})
        report = validate(load_dataset(str(dataset_dir)))
        assert any("unknown filter key" in error for error in report.errors)

    def test_cli_validate_success_and_failure(self, capsys, tmp_path):
        dataset_dir = write_dataset(tmp_path)
        code, envelope = run(capsys, ["eval", "validate", "--dataset", str(dataset_dir)])
        assert code == 0
        assert envelope["result"]["valid"] is True
        assert envelope["meta"]["subcommand"] == "validate"

        rewrite_query(dataset_dir, "q3", gold_facts=["Sneaky fact."])
        code, envelope = run(capsys, ["eval", "validate", "--dataset", str(dataset_dir)])
        assert code == 1
        assert envelope["error"]["type"] == "contract_violation"
        assert envelope["error"]["details"]["errors"]

    def test_cli_missing_dataset_is_not_found(self, capsys, tmp_path):
        code, envelope = run(
            capsys, ["eval", "validate", "--dataset", str(tmp_path / "nope")]
        )
        assert code == 1
        assert envelope["error"]["type"] == "not_found"

    def test_cli_eval_without_subcommand(self, capsys):
        code, envelope = run(capsys, ["eval"])
        assert code == 1
        assert envelope["error"]["type"] == "invalid_arguments"


def make_query(**overrides):
    query = {
        "id": "q",
        "query": "?",
        "answerable": True,
        "category": "known_item",
        "slices": [],
        "relevant_evidence": [
            {"note_id": "A", "path": "a.md", "heading": "One", "grade": 3},
            {"note_id": "A", "path": "a.md", "heading": "Two", "grade": 2},
            {"note_id": "B", "path": "b.md", "heading": "Zero", "grade": 0},
        ],
        "required_evidence_groups": [["A#One"], ["A#Two"]],
        "gold_facts": ["f"],
        "forbidden_facts": [],
    }
    query.update(overrides)
    return query


def candidate(path, heading, chunk_id="x::s000"):
    return {"path": path, "heading": heading, "chunk_id": chunk_id}


class TestScoring:
    def test_perfect_ranking(self):
        candidates = [candidate("a.md", "One"), candidate("a.md", "Two")]
        score = score_retrieval(make_query(), candidates, k=5)
        assert score["ndcg_at_k"] == 1.0
        assert score["group_recall_at_k"] == 1.0
        assert score["complete_at_k"] is True
        assert score["first_grade3_rank"] == 1
        assert score["reciprocal_rank"] == 1.0
        assert score["missed"] == []

    def test_grade0_hard_negative_earns_nothing(self):
        candidates = [candidate("b.md", "Zero"), candidate("a.md", "One")]
        score = score_retrieval(make_query(), candidates, k=5)
        assert score["first_grade3_rank"] == 2
        assert score["reciprocal_rank"] == 0.5
        assert score["group_recall_at_k"] == 0.5
        assert score["complete_at_k"] is False
        assert score["unsatisfied_groups"] == [["A#Two"]]

    def test_miss_outside_k_does_not_count(self):
        candidates = [candidate("b.md", "Zero")] * 5 + [candidate("a.md", "One")]
        score = score_retrieval(make_query(), candidates, k=5)
        assert score["ndcg_at_k"] == 0.0
        assert score["complete_at_k"] is False
        # ...but the reciprocal rank still sees the late hit.
        assert score["first_grade3_rank"] == 6

    def test_document_candidate_covers_all_headings(self):
        candidates = [candidate("a.md", "", chunk_id="A::doc")]
        score = score_retrieval(make_query(), candidates, k=5)
        # One doc candidate claims the best label and satisfies both groups.
        assert score["group_recall_at_k"] == 1.0
        assert score["complete_at_k"] is True
        assert score["matched"][0]["grade"] == 3

    def test_note_level_collapse(self):
        candidates = [candidate("a.md", "", chunk_id="A::doc")]
        score = score_retrieval(make_query(), candidates, k=5, note_level=True)
        # Labels collapse to one note-level unit, so a single doc hit is perfect.
        assert score["ndcg_at_k"] == 1.0
        assert score["complete_at_k"] is True

    def test_empty_candidates_score_zero(self):
        score = score_retrieval(make_query(), [], k=5)
        assert score["ndcg_at_k"] == 0.0
        assert score["group_recall_at_k"] == 0.0
        assert score["reciprocal_rank"] == 0.0
        assert len(score["missed"]) == 2


class JudgeAwareProvider(FakeProvider):
    """Fake provider whose chat answers synthesis and judge prompts differently."""

    def chat(self, system_prompt, user_prompt, temperature=0.2, max_tokens=1024, model=None):
        if "evaluation judge" in system_prompt:
            statements = re.findall(r"^\d+\. ", user_prompt, re.M)
            return json.dumps({"verdicts": [True] * len(statements)})
        return self.chat_response


class TestRunCli:
    def sync(self, capsys, monkeypatch, tmp_path, dataset_dir, provider=None):
        provider = provider or FakeProvider()
        monkeypatch.setattr(cli, "get_provider", lambda: provider)
        chroma = str(tmp_path / "chroma")
        code, envelope = run(
            capsys,
            ["--chroma-path", chroma, "sync", "--root", str(dataset_dir / "corpus")],
        )
        assert code == 0, envelope
        return chroma

    def test_retrieval_stage(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        chroma = self.sync(capsys, monkeypatch, tmp_path, dataset_dir)

        code, envelope = run(
            capsys,
            ["--chroma-path", chroma, "eval", "run", "--dataset", str(dataset_dir)],
        )
        assert code == 0, envelope
        result = envelope["result"]
        assert result["results_schema_version"] == 1
        assert result["dataset"]["name"] == "test-eval"
        assert result["run"]["stage"] == "retrieval"
        assert result["aggregates"]["retrieval"]["queries_scored"] == 2

        by_id = {entry["id"]: entry for entry in result["queries"]}
        assert "skipped" in by_id["q3"]
        # q2 filters to type=runbook, leaving only the Beta note in the pool.
        assert by_id["q2"]["retrieval"]["complete_at_k"] is True
        assert "known_item" in result["by_category"]
        assert "type_filter" in result["by_slice"]

    def test_out_writes_results_file(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        chroma = self.sync(capsys, monkeypatch, tmp_path, dataset_dir)
        out = tmp_path / "results.json"

        code, envelope = run(
            capsys,
            [
                "--chroma-path", chroma, "eval", "run",
                "--dataset", str(dataset_dir), "--out", str(out),
            ],
        )
        assert code == 0
        assert envelope["meta"]["out"] == str(out)
        written = json.loads(out.read_text())
        assert written["results_schema_version"] == 1

    def test_only_filters_and_rejects_unknown(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        chroma = self.sync(capsys, monkeypatch, tmp_path, dataset_dir)

        code, envelope = run(
            capsys,
            [
                "--chroma-path", chroma, "eval", "run",
                "--dataset", str(dataset_dir), "--only", "q1",
            ],
        )
        assert code == 0
        assert [entry["id"] for entry in envelope["result"]["queries"]] == ["q1"]

        code, envelope = run(
            capsys,
            [
                "--chroma-path", chroma, "eval", "run",
                "--dataset", str(dataset_dir), "--only", "q99",
            ],
        )
        assert code == 1
        assert envelope["error"]["type"] == "invalid_arguments"

    def test_index_mismatch_is_config_mismatch(self, capsys, tmp_path, monkeypatch, tiny_vault):
        dataset_dir = write_dataset(tmp_path)
        provider = FakeProvider()
        monkeypatch.setattr(cli, "get_provider", lambda: provider)
        chroma = str(tmp_path / "chroma")
        run(capsys, ["--chroma-path", chroma, "sync", "--root", str(tiny_vault)])

        code, envelope = run(
            capsys,
            ["--chroma-path", chroma, "eval", "run", "--dataset", str(dataset_dir)],
        )
        assert code == 1
        assert envelope["error"]["type"] == "config_mismatch"
        assert envelope["error"]["details"]["missing_from_index"]

    def test_empty_index_is_index_empty(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        monkeypatch.setattr(cli, "get_provider", lambda: FakeProvider())

        code, envelope = run(
            capsys,
            [
                "--chroma-path", str(tmp_path / "chroma"), "eval", "run",
                "--dataset", str(dataset_dir),
            ],
        )
        assert code == 1
        assert envelope["error"]["type"] == "index_empty"

    def test_synthesis_stage_scores_abstention_and_facts(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        provider = JudgeAwareProvider()
        chroma = self.sync(capsys, monkeypatch, tmp_path, dataset_dir, provider)

        code, envelope = run(
            capsys,
            [
                "--chroma-path", chroma, "eval", "run",
                "--dataset", str(dataset_dir), "--stage", "synthesis",
            ],
        )
        assert code == 0, envelope
        result = envelope["result"]
        assert result["run"]["stage"] == "synthesis"

        by_id = {entry["id"]: entry for entry in result["queries"]}
        # The canned answer never abstains: correct for q1/q2, wrong for q3.
        assert by_id["q1"]["synthesis"]["abstention_correct"] is True
        assert by_id["q3"]["synthesis"]["abstention_correct"] is False
        # The all-true judge grants every gold fact and flags q1's forbidden fact.
        assert by_id["q1"]["synthesis"]["gold_fact_coverage"] == 1.0
        assert by_id["q1"]["synthesis"]["forbidden_facts_present"]

        synthesis = result["aggregates"]["synthesis"]
        assert synthesis["queries_scored"] == 3
        assert synthesis["abstention_accuracy"] == round(2 / 3, 4)
        assert synthesis["false_answer_rate"] == 1.0
        assert synthesis["gold_fact_coverage"] == 1.0
        assert synthesis["judge_failures"] == 0

    def test_synthesis_abstains_correctly_on_unanswerable(self, capsys, tmp_path, monkeypatch):
        dataset_dir = write_dataset(tmp_path)
        provider = JudgeAwareProvider()
        provider.chat_response = json.dumps(
            {"answer": "", "citations": [], "confidence": "Low", "abstained": True}
        )
        chroma = self.sync(capsys, monkeypatch, tmp_path, dataset_dir, provider)

        code, envelope = run(
            capsys,
            [
                "--chroma-path", chroma, "eval", "run",
                "--dataset", str(dataset_dir), "--stage", "synthesis", "--only", "q3",
            ],
        )
        assert code == 0
        entry = envelope["result"]["queries"][0]
        assert entry["synthesis"]["abstained"] is True
        assert entry["synthesis"]["abstention_correct"] is True
        assert envelope["result"]["aggregates"]["synthesis"]["false_answer_rate"] == 0.0
