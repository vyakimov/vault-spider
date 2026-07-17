"""Smoke tests for the stable vault-spider wrapper entrypoint."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "bin" / "vault-spider"
MCP_WRAPPER = REPO_ROOT / "bin" / "vault-spider-mcp"


def test_wrapper_forwards_argv_and_exit_status_from_outside_repo(tmp_path: Path) -> None:
    assert os.access(WRAPPER, os.X_OK)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))\n"
        "sys.exit(23)\n",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)

    caller_dir = tmp_path / "caller"
    caller_dir.mkdir()
    env = os.environ.copy()
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")

    completed = subprocess.run(
        [str(WRAPPER), "retrieve", "--query", "two words"],
        cwd=caller_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 23
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == {
        "argv": [
            "run",
            "--project",
            str(REPO_ROOT),
            "vault-spider",
            "retrieve",
            "--query",
            "two words",
        ],
        "cwd": str(caller_dir),
    }


def test_mcp_wrapper_forwards_transport_from_outside_repo(tmp_path: Path) -> None:
    assert os.access(MCP_WRAPPER, os.X_OK)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))\n",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)
    caller_dir = tmp_path / "caller"
    caller_dir.mkdir()
    env = os.environ.copy()
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")

    completed = subprocess.run(
        [str(MCP_WRAPPER), "--transport", "streamable-http", "--port", "9123"],
        cwd=caller_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert json.loads(completed.stdout) == {
        "argv": [
            "run",
            "--project",
            str(REPO_ROOT),
            "vault-spider-mcp",
            "--transport",
            "streamable-http",
            "--port",
            "9123",
        ],
        "cwd": str(caller_dir),
    }
