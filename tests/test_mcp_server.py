"""Network-free tests for the MCP adapter and generated tool contracts."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from vault_spider import mcp_server


def test_run_cli_uses_project_cwd_and_preserves_failure_envelopes(monkeypatch) -> None:
    expected = {
        "ok": False,
        "action": "stats",
        "error": {"type": "index_empty", "message": "empty"},
    }

    def fake_run(argv, **kwargs):
        assert argv == [
            sys.executable,
            "-m",
            "vault_spider.cli",
            "--collection",
            "test-notes",
            "stats",
        ]
        assert kwargs["cwd"] == mcp_server.REPO_ROOT
        assert kwargs["capture_output"] is True
        assert kwargs["check"] is False
        return subprocess.CompletedProcess(argv, 1, json.dumps(expected), "")

    monkeypatch.setattr(mcp_server, "_cli_prefix", ["--collection", "test-notes"])
    monkeypatch.setattr(mcp_server.subprocess, "run", fake_run)

    assert mcp_server._run_cli(["stats"]) == expected


def test_run_cli_fails_closed_on_non_json_stdout(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "_cli_prefix", [])
    monkeypatch.setattr(
        mcp_server.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 2, "noise", "bad"),
    )

    envelope = mcp_server._run_cli(["retrieve", "--query", "test"])

    assert envelope["ok"] is False
    assert envelope["action"] == "retrieve"
    assert envelope["error"]["type"] == "internal_error"
    assert envelope["error"]["details"] == {"exit_code": 2, "stderr": "bad"}


def test_search_tool_maps_filters_to_cli_arguments(monkeypatch) -> None:
    monkeypatch.setattr(mcp_server, "_run_cli", lambda arguments: {"arguments": arguments})

    result = mcp_server.search_vault(
        "network setup",
        mode="thorough",
        granularity="mixed",
        limit=7,
        folder="Projects",
        tags=["network", "ops"],
        note_type="reference",
        since="2026-01-01",
        until="2026-07-01",
        must_include=["wireguard", "dns"],
    )

    assert result["arguments"] == [
        "retrieve",
        "--query",
        "network setup",
        "--mode",
        "thorough",
        "--granularity",
        "mixed",
        "-n",
        "7",
        "--folder",
        "Projects",
        "--tag",
        "network",
        "--tag",
        "ops",
        "--type",
        "reference",
        "--since",
        "2026-01-01",
        "--until",
        "2026-07-01",
        "--must-include",
        "wireguard",
        "--must-include",
        "dns",
    ]


def test_mutation_tools_default_to_dry_run_and_encode_structured_inputs(monkeypatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        mcp_server,
        "_run_cli",
        lambda arguments: calls.append(arguments) or {"ok": True},
    )

    mcp_server.create_note(
        "Inbox/Test.md",
        content="Draft",
        frontmatter={"type": "idea"},
    )
    mcp_server.add_links(
        "Inbox/Test.md",
        [mcp_server.LinkSpec(target="Related Note", anchor_text="related", line=3)],
    )
    mcp_server.edit_note(
        "Inbox/Test.md",
        [mcp_server.TextEdit(old_text="Draft", new_text="Revised")],
    )

    assert calls[0][-2:] == ["--auto-id", "--dry-run"]
    assert json.loads(calls[0][calls[0].index("--frontmatter") + 1]) == {"type": "idea"}
    assert calls[1][-1] == "--dry-run"
    assert json.loads(calls[1][calls[1].index("--links") + 1]) == [
        {"target": "Related Note", "anchor_text": "related", "line": 3}
    ]
    assert calls[2][-1] == "--dry-run"
    assert json.loads(calls[2][calls[2].index("--edits") + 1]) == [
        {"old_text": "Draft", "new_text": "Revised"}
    ]


def test_generated_tools_expose_safety_annotations_and_bounded_schemas() -> None:
    tools = {tool.name: tool for tool in asyncio.run(mcp_server.mcp.list_tools())}

    assert set(tools) == {
        "vault_stats",
        "sync_index",
        "search_vault",
        "answer_from_vault",
        "lint_vault",
        "plan_enrichment",
        "read_note",
        "edit_note",
        "create_note",
        "merge_frontmatter",
        "add_links",
        "insert_related",
        "move_note",
        "rename_note",
        "open_note",
    }
    search_annotations = tools["search_vault"].annotations
    create_annotations = tools["create_note"].annotations
    assert search_annotations is not None
    assert create_annotations is not None
    assert search_annotations.readOnlyHint is True
    assert search_annotations.openWorldHint is True
    assert create_annotations.readOnlyHint is False
    assert create_annotations.destructiveHint is True
    assert tools["create_note"].inputSchema["properties"]["dry_run"]["default"] is True
    assert tools["edit_note"].inputSchema["properties"]["dry_run"]["default"] is True
    assert tools["edit_note"].inputSchema["properties"]["edits"]["minItems"] == 1
    assert tools["search_vault"].inputSchema["properties"]["limit"] == {
        "default": 10,
        "maximum": 50,
        "minimum": 1,
        "title": "Limit",
        "type": "integer",
    }


def test_stdio_protocol_exposes_tools() -> None:
    async def discover() -> tuple[str, set[str]]:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "vault_spider.mcp_server"],
            cwd=Path(__file__).resolve().parents[1],
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                initialized = await session.initialize()
                tools = await session.list_tools()
                return initialized.serverInfo.name, {tool.name for tool in tools.tools}

    name, tools = asyncio.run(discover())

    assert name == "Vault Spider"
    assert {"search_vault", "answer_from_vault", "create_note", "read_note", "edit_note"} <= tools


def test_main_configures_http_transport_and_cli_overrides(monkeypatch) -> None:
    class FakeServer:
        def run(self, *, transport):
            assert transport == "streamable-http"

    monkeypatch.setattr(
        mcp_server,
        "create_server",
        lambda *, host, port: (
            FakeServer()
            if (host, port) == ("0.0.0.0", 9123)
            else (_ for _ in ()).throw(AssertionError((host, port)))
        ),
    )

    mcp_server.main(
        [
            "--transport",
            "streamable-http",
            "--host",
            "0.0.0.0",
            "--port",
            "9123",
            "--chroma-path",
            "other-db",
            "--collection",
            "other-notes",
        ]
    )

    assert mcp_server._cli_prefix == [
        "--chroma-path",
        str(Path.cwd() / "other-db"),
        "--collection",
        "other-notes",
    ]
