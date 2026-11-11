#!/usr/bin/env python3
"""Run serialized Vault Spider maintenance for launchd.

The default job performs an incremental sync only. Set
``VAULT_SPIDER_RUN_LINT=1`` (or pass ``--lint``) to run the read-only lint
report after a successful sync. Full command envelopes are kept in a private
per-user state directory while launchd receives compact JSON-line events.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MaintenanceError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _event(name: str, **fields: Any) -> None:
    print(json.dumps({"time": _now(), "event": name, **fields}, sort_keys=True), flush=True)


def _enabled(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _state_dir() -> Path:
    configured = os.environ.get("VAULT_SPIDER_MAINTENANCE_STATE")
    path = (
        Path(configured).expanduser()
        if configured
        else Path.home() / "Library" / "Caches" / "VaultSpider"
    )
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


def _atomic_json(path: Path, payload: Dict[str, Any]) -> None:
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        temporary.chmod(0o600)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _run_command(wrapper: Path, repo: Path, action: str) -> Tuple[int, Dict[str, Any]]:
    started = time.monotonic()
    try:
        process = subprocess.run(
            [str(wrapper), action],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise MaintenanceError(f"cannot run {wrapper}: {exc}") from exc

    if process.stderr:
        print(process.stderr.rstrip(), file=sys.stderr, flush=True)
    output = process.stdout.strip()
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise MaintenanceError(
            f"{action} returned non-JSON stdout (exit {process.returncode}): {output[:500]}"
        ) from exc
    if not isinstance(payload, dict):
        raise MaintenanceError(f"{action} returned a non-object JSON envelope")
    payload["maintenance"] = {
        "completed_at": _now(),
        "duration_ms": round((time.monotonic() - started) * 1000, 2),
        "exit_code": process.returncode,
    }
    return process.returncode, payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Vault Spider repository root (default: parent of this script)",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run read-only vault lint after a successful sync",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    repo = args.repo.expanduser().resolve()
    wrapper = repo / "bin" / "vault-spider"
    lint_enabled = args.lint or _enabled(os.environ.get("VAULT_SPIDER_RUN_LINT"))

    try:
        if not wrapper.is_file() or not os.access(wrapper, os.X_OK):
            raise MaintenanceError(f"executable wrapper not found: {wrapper}")
        state = _state_dir()
        with (state / "maintenance.lock").open("a+", encoding="utf-8") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                _event("maintenance_skipped", reason="another run is active")
                return 0

            _event("maintenance_started", repo=str(repo), lint_enabled=lint_enabled)
            sync_code, sync_payload = _run_command(wrapper, repo, "sync")
            _atomic_json(state / "last-sync.json", sync_payload)
            _event(
                "sync_completed",
                ok=bool(sync_payload.get("ok")) and sync_code == 0,
                exit_code=sync_code,
                result=sync_payload.get("result"),
                error=sync_payload.get("error"),
                duration_ms=sync_payload["maintenance"]["duration_ms"],
            )
            if sync_code != 0 or not sync_payload.get("ok"):
                return sync_code or 1

            if lint_enabled:
                lint_code, lint_payload = _run_command(wrapper, repo, "lint")
                _atomic_json(state / "last-lint.json", lint_payload)
                lint_result = lint_payload.get("result") or {}
                _event(
                    "lint_completed",
                    ok=bool(lint_payload.get("ok")) and lint_code == 0,
                    exit_code=lint_code,
                    root=lint_result.get("root"),
                    notes_scanned=lint_result.get("notes_scanned"),
                    summary=lint_result.get("summary"),
                    error=lint_payload.get("error"),
                    duration_ms=lint_payload["maintenance"]["duration_ms"],
                )
                if lint_code != 0 or not lint_payload.get("ok"):
                    return lint_code or 1

            _event("maintenance_completed", ok=True)
            return 0
    except (OSError, MaintenanceError) as exc:
        _event("maintenance_failed", error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
