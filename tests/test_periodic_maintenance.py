"""Tests for the launchd maintenance runner without a real vault or provider."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import periodic_maintenance  # pyright: ignore[reportMissingImports]  # noqa: E402


def make_repo(tmp_path: Path, sync_ok: bool = True) -> Path:
    repo = tmp_path / "repo"
    wrapper = repo / "bin" / "vault-spider"
    wrapper.parent.mkdir(parents=True)
    wrapper.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"sync_ok = {sync_ok!r}\n"
        "action = sys.argv[1]\n"
        "if action == 'sync':\n"
        "    payload = ({'ok': True, 'action': 'sync', 'result': "
        "{'added_notes': 0, 'updated_notes': 0, 'deleted_notes': 0, 'unchanged': 26}} "
        "if sync_ok else {'ok': False, 'action': 'sync', "
        "'error': {'type': 'provider_error', 'message': 'offline'}})\n"
        "elif action == 'lint':\n"
        "    payload = {'ok': True, 'action': 'lint', 'result': "
        "{'root': '/fixture', 'notes_scanned': 26, 'summary': {'broken_wikilinks': 0}}}\n"
        "else:\n"
        "    payload = {'ok': False, 'action': action}\n"
        "print(json.dumps(payload))\n"
        "sys.exit(0 if payload['ok'] else 1)\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    return repo


def events(capsys) -> list[dict]:
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def test_sync_only_writes_private_latest_envelope(tmp_path, monkeypatch, capsys):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    monkeypatch.setenv("VAULT_SPIDER_MAINTENANCE_STATE", str(state))
    monkeypatch.delenv("VAULT_SPIDER_RUN_LINT", raising=False)

    code = periodic_maintenance.main(["--repo", str(repo)])
    output = events(capsys)

    assert code == 0
    assert [item["event"] for item in output] == [
        "maintenance_started",
        "sync_completed",
        "maintenance_completed",
    ]
    assert output[1]["result"]["unchanged"] == 26
    saved = json.loads((state / "last-sync.json").read_text(encoding="utf-8"))
    assert saved["ok"] is True
    assert (state.stat().st_mode & 0o777) == 0o700
    assert ((state / "last-sync.json").stat().st_mode & 0o777) == 0o600
    assert not (state / "last-lint.json").exists()


def test_opt_in_lint_records_summary_and_full_envelope(tmp_path, monkeypatch, capsys):
    repo = make_repo(tmp_path)
    state = tmp_path / "state"
    monkeypatch.setenv("VAULT_SPIDER_MAINTENANCE_STATE", str(state))
    monkeypatch.setenv("VAULT_SPIDER_RUN_LINT", "true")

    code = periodic_maintenance.main(["--repo", str(repo)])
    output = events(capsys)

    assert code == 0
    assert [item["event"] for item in output] == [
        "maintenance_started",
        "sync_completed",
        "lint_completed",
        "maintenance_completed",
    ]
    assert output[2]["summary"] == {"broken_wikilinks": 0}
    assert json.loads((state / "last-lint.json").read_text(encoding="utf-8"))["ok"] is True


def test_sync_failure_stops_before_lint(tmp_path, monkeypatch, capsys):
    repo = make_repo(tmp_path, sync_ok=False)
    state = tmp_path / "state"
    monkeypatch.setenv("VAULT_SPIDER_MAINTENANCE_STATE", str(state))
    monkeypatch.setenv("VAULT_SPIDER_RUN_LINT", "1")

    code = periodic_maintenance.main(["--repo", str(repo)])
    output = events(capsys)

    assert code == 1
    assert [item["event"] for item in output] == [
        "maintenance_started",
        "sync_completed",
    ]
    assert output[1]["error"]["type"] == "provider_error"
    assert not (state / "last-lint.json").exists()
