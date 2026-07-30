"""Tests for canonical note-level retrieval summaries."""

from __future__ import annotations

import json

import pytest

from vault_spider import cli
from vault_spider.corpus.loader import Note, load_notes
from vault_spider.index.context_summaries import (
    ContextSummaryError,
    SummaryStore,
    import_jobs,
    prepare_jobs,
    summary_fingerprint,
    summary_status,
)


def make_note(
    note_id: str = "note-1",
    *,
    path: str = "Topic.md",
    title: str = "Topic",
    body: str = "# Topic\nA useful detail.",
) -> Note:
    return Note(
        note_id=note_id,
        path=path,
        title=title,
        tags=[],
        created=None,
        updated=None,
        date="",
        note_type="",
        body=body,
        raw_text=body,
        content_hash="raw",
    )


def complete_jobs(path, summary: str = "A concise factual note summary.") -> None:
    for job_path in path.glob("*.json"):
        payload = json.loads(job_path.read_text(encoding="utf-8"))
        payload["summary"] = summary
        payload["generated_by"] = "codex"
        job_path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )


def test_prepare_import_and_status_round_trip(tmp_path):
    note = make_note()
    jobs = tmp_path / "jobs"
    store = SummaryStore(str(tmp_path / "summaries"))

    prepared = prepare_jobs([note], str(jobs), store)
    assert prepared["prepared"] == ["Topic.md"]
    job_path = next(jobs.glob("*.json"))
    job = json.loads(job_path.read_text(encoding="utf-8"))
    assert job["note_id"] == note.note_id
    assert job["source_fingerprint"] == summary_fingerprint(note)
    assert job["body"] == note.body
    assert job["summary"] == ""
    assert "untrusted" in job["instructions"]

    complete_jobs(jobs)
    imported = import_jobs(str(jobs), store)
    assert imported["imported"] == 1
    resolution = store.resolve(note)
    assert resolution.status == "ready"
    assert resolution.summary == "A concise factual note summary."

    status = summary_status([note], store)
    assert status["ready_count"] == 1
    assert status["coverage"] == 1.0


def test_path_move_does_not_stale_summary_but_body_edit_does(tmp_path):
    original = make_note()
    jobs = tmp_path / "jobs"
    store = SummaryStore(str(tmp_path / "summaries"))
    prepare_jobs([original], str(jobs), store)
    complete_jobs(jobs)
    import_jobs(str(jobs), store)

    moved = make_note(path="Archive/Topic.md")
    changed = make_note(body="# Topic\nA different detail.")

    assert store.resolve(moved).status == "ready"
    assert store.resolve(changed).status == "stale"


def test_prepare_preserves_an_existing_job_for_the_same_snapshot(tmp_path):
    note = make_note()
    jobs = tmp_path / "jobs"
    store = SummaryStore(str(tmp_path / "summaries"))
    prepare_jobs([note], str(jobs), store)
    complete_jobs(jobs, "Work already completed.")

    second = prepare_jobs([note], str(jobs), store)

    assert second["existing_jobs"] == ["Topic.md"]
    payload = json.loads(next(jobs.glob("*.json")).read_text(encoding="utf-8"))
    assert payload["summary"] == "Work already completed."


def test_import_validates_the_complete_batch_before_writing(tmp_path):
    notes = [make_note("one"), make_note("two", path="Two.md", title="Two")]
    jobs = tmp_path / "jobs"
    store = SummaryStore(str(tmp_path / "summaries"))
    prepare_jobs(notes, str(jobs), store)
    first, _second = sorted(jobs.glob("*.json"))
    payload = json.loads(first.read_text(encoding="utf-8"))
    payload["summary"] = "Only one job was completed."
    first.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ContextSummaryError, match="summary must not be empty"):
        import_jobs(str(jobs), store)

    assert store.records() == []


def test_cli_workflow_needs_no_provider(
    tmp_path, capsys, monkeypatch, isolated_config
):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "Topic.md").write_text("# Topic\nA detail.", encoding="utf-8")
    jobs = tmp_path / "jobs"
    summaries = tmp_path / "summaries"
    monkeypatch.setattr(
        cli,
        "get_provider",
        lambda: (_ for _ in ()).throw(AssertionError("provider should not load")),
    )

    code = cli.main(
        [
            "context",
            "prepare",
            "--root",
            str(vault),
            "--out",
            str(jobs),
            "--store",
            str(summaries),
        ]
    )
    prepared = json.loads(capsys.readouterr().out)
    assert code == 0
    assert prepared["result"]["prepared_count"] == 1

    complete_jobs(jobs)
    code = cli.main(
        [
            "context",
            "import",
            "--from",
            str(jobs),
            "--store",
            str(summaries),
        ]
    )
    imported = json.loads(capsys.readouterr().out)
    assert code == 0
    assert imported["result"]["imported"] == 1

    code = cli.main(
        [
            "context",
            "status",
            "--root",
            str(vault),
            "--store",
            str(summaries),
        ]
    )
    status = json.loads(capsys.readouterr().out)
    assert code == 0
    assert status["result"]["ready_count"] == 1
    assert [note.path for note in load_notes(str(vault))] == ["Topic.md"]
