"""Tests for the web routes.

Network-free: the app is built with a fake provider and a temp vault + index, so no
API key and no OpenRouter call is involved.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from chromadb.errors import InternalError as ChromaInternalError
from conftest import FakeProvider
from fastapi.testclient import TestClient

from vault_spider.index.store import IndexStore
from vault_spider.retrieval.searcher import Searcher
from vault_spider.web.app import create_app
from vault_spider.web.state import AppState


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def web_vault(tmp_path) -> Path:
    vault = tmp_path / "vault"
    write(
        vault / "Infra/VPN.md",
        "---\ntitle: WireGuard setup\ntype: technote\nprovenance: human\n"
        "updated: 2026-01-15T10:00:00Z\ntags: [infra, vpn]\naliases: [The VPN]\n---\n"
        "# WireGuard setup\n\n"
        "Intro about the tunnel and [[Hosts]] and [[Nowhere]].\n\n"
        "> [!NOTE] Watch out\n> The key rotates.\n\n"
        "## Key rotation\n\nRotate every 90 days. Run `wg genkey` on $HOME.\n",
    )
    write(
        vault / "Infra/Hosts.md",
        "---\ntitle: Hosts\n---\n\nThe host list, see [[WireGuard setup]].\n",
    )
    write(vault / "secret.md", "---\ntitle: Secret\ntags: [secret]\n---\nClassified.\n")
    write(vault / "Templates/T.md", "A template.\n")
    (vault / "assets").mkdir(parents=True, exist_ok=True)
    (vault / "assets" / "pic.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return vault


@pytest.fixture
def client_for(web_vault, tmp_path):
    """Build a test client, optionally with an Obsidian vault name pinned on the state."""
    provider = FakeProvider()
    store = IndexStore(chroma_db_path=str(tmp_path / "chroma"), provider=provider)
    store.sync(str(web_vault))

    @contextmanager
    def build(vault_name=None):
        def factory() -> AppState:
            return AppState(
                vault_root=str(web_vault),
                provider=provider,
                store=store,
                searcher=Searcher(store, granularity="document", provider=provider),
                vault_name=vault_name,
            )

        with TestClient(create_app(state_factory=factory)) as test_client:
            yield test_client

    return build


@pytest.fixture
def client(client_for):
    with client_for() as test_client:
        yield test_client


@pytest.fixture
def named_client(client_for):
    """A client whose vault resolves a name, so `obsidian://` links can form."""
    with client_for(vault_name="Test Vault") as test_client:
        yield test_client


class TestIndexPage:
    def test_renders_without_a_query(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Ask the vault" in response.text
        assert "notes" in response.text

    def test_query_returns_results(self, client):
        response = client.get("/", params={"q": "wireguard tunnel"})
        assert response.status_code == 200
        assert "WireGuard setup" in response.text
        assert "/note/Infra/VPN.md" in response.text

    def test_results_are_bookmarkable(self, client):
        """A reload of the same URL reproduces the same page."""
        url = "/?q=wireguard+tunnel&mode=fast&granularity=document&n=3"
        first, second = client.get(url), client.get(url)
        assert first.status_code == second.status_code == 200
        assert "WireGuard setup" in second.text

    def test_unknown_knobs_fall_back_to_defaults(self, client):
        response = client.get("/", params={"q": "x", "mode": "evil", "granularity": "evil"})
        assert response.status_code == 200
        assert "fast · document" in response.text

    def test_result_count_is_clamped(self, client):
        response = client.get("/", params={"q": "x", "n": "9999"})
        assert response.status_code == 200
        assert "· 50" in response.text

    def test_excerpts_are_not_raw_markdown(self, client):
        response = client.get("/", params={"q": "wireguard tunnel"})
        body = response.text.split('class="result__excerpt"')[-1]
        assert "[[" not in body


class TestNotePage:
    def test_renders_the_note(self, client):
        response = client.get("/note/Infra/VPN.md")
        assert response.status_code == 200
        assert "WireGuard setup" in response.text
        assert "Rotate every 90 days" in response.text

    def test_shows_frontmatter_as_a_masthead_not_prose(self, client):
        text = client.get("/note/Infra/VPN.md").text
        assert "human" in text and "technote" in text
        # The synthesized indexing header must never appear in the reading view.
        assert "Path: Infra/VPN.md" not in text

    def test_resolved_and_unresolved_wikilinks(self, client):
        text = client.get("/note/Infra/VPN.md").text
        assert '<a href="/note/Infra/Hosts.md" class="wikilink">Hosts</a>' in text
        assert 'class="wikilink wikilink--missing"' in text
        assert ">Nowhere</span>" in text

    def test_callout_renders(self, client):
        text = client.get("/note/Infra/VPN.md").text
        assert 'class="callout callout--note"' in text
        assert "Watch out" in text

    def test_backlinks_are_listed(self, client):
        text = client.get("/note/Infra/VPN.md").text
        assert "Linked from" in text
        assert "/note/Infra/Hosts.md" in text

    def test_highlight_range_marks_the_body(self, client):
        response = client.get("/note/Infra/VPN.md", params={"from": 3, "to": 3})
        assert 'id="L3"' in response.text
        assert "is-match" in response.text

    def test_bad_highlight_range_is_ignored(self, client):
        response = client.get("/note/Infra/VPN.md", params={"from": "abc", "to": "-2"})
        assert response.status_code == 200
        assert "is-match" not in response.text

    def test_missing_note_is_404(self, client):
        assert client.get("/note/Nope.md").status_code == 404

    def test_secret_note_is_404(self, client):
        """A `#secret`-tagged note must not be readable through the web app."""
        assert client.get("/note/secret.md").status_code == 404

    def test_skipped_directory_is_404(self, client):
        assert client.get("/note/Templates/T.md").status_code == 404

    @pytest.mark.parametrize("path", ["../../etc/passwd", "a/../../b.md"])
    def test_traversal_is_rejected(self, client, path):
        response = client.get(f"/note/{path}")
        assert response.status_code in (400, 404)
        assert "root:" not in response.text


class TestAttachments:
    def test_serves_a_vault_file(self, client):
        response = client.get("/attachment/assets/pic.png")
        assert response.status_code == 200
        assert response.content.startswith(b"\x89PNG")

    def test_missing_attachment_is_404(self, client):
        assert client.get("/attachment/assets/nope.png").status_code == 404

    def test_skipped_directory_is_404(self, client):
        assert client.get("/attachment/Templates/T.md").status_code == 404


class TestObsidianLinks:
    def test_results_offer_an_obsidian_link(self, named_client):
        body = named_client.get("/", params={"q": "wireguard"}).text
        assert 'class="result__obsidian"' in body
        assert "obsidian://open?vault=Test%20Vault&amp;file=" in body

    def test_link_is_absent_without_a_vault_name(self, client):
        """No name resolved means no link — the results themselves are unaffected."""
        body = client.get("/", params={"q": "wireguard"}).text
        assert "result__obsidian" not in body
        assert "obsidian://" not in body
        assert 'class="result__path"' in body

    def test_api_carries_the_link_for_each_candidate(self, named_client):
        payload = named_client.get("/api/retrieve", params={"q": "wireguard"}).json()
        urls = [c["obsidian_url"] for c in payload["result"]["candidates"]]
        assert urls and all(u.startswith("obsidian://open?vault=Test%20Vault&file=") for u in urls)


class TestJsonApi:
    def test_retrieve_matches_the_cli_contract(self, client):
        response = client.get("/api/retrieve", params={"q": "wireguard", "n": 2})
        assert response.status_code == 200
        payload = response.json()
        assert payload["ok"] is True
        assert payload["action"] == "retrieve"
        assert set(payload["result"]) == {"query", "mode", "granularity", "candidates"}
        candidate = payload["result"]["candidates"][0]
        assert set(candidate) == {
            "note_id", "path", "obsidian_url", "title", "type", "provenance", "heading",
            "chunk_id", "line_start", "line_end", "excerpt", "scores", "graph", "why",
        }
        # Nullable and additive: an ordinary candidate carries the key set to null.
        assert candidate["graph"] is None
        assert set(candidate["scores"]) == {"bm25", "semantic", "fused", "reranker", "final"}

    def test_excerpt_is_the_untouched_contract_value(self, client):
        """The JSON route serves `build_retrieval_output` verbatim, header and all."""
        payload = client.get("/api/retrieve", params={"q": "wireguard"}).json()
        excerpts = [c["excerpt"] for c in payload["result"]["candidates"]]
        assert any(text.startswith("# ") and "\nPath: " in text for text in excerpts)

    def test_missing_query_is_a_400_envelope(self, client):
        response = client.get("/api/retrieve")
        assert response.status_code == 400
        payload = response.json()
        assert payload["ok"] is False
        assert payload["error"]["type"] == "invalid_arguments"

    def test_note_route(self, client):
        payload = client.get("/api/note/Infra/VPN.md").json()
        assert payload["ok"] is True
        assert payload["result"]["title"] == "WireGuard setup"
        assert payload["result"]["backlinks"] == ["Infra/Hosts.md"]

    def test_note_route_404_envelope(self, client):
        response = client.get("/api/note/Nope.md")
        assert response.status_code == 404
        assert response.json()["error"]["type"] == "not_found"


class TestAnswer:
    def test_htmx_request_gets_a_fragment(self, client):
        response = client.post(
            "/answer",
            data={"q": "wireguard", "mode": "fast", "granularity": "document", "n": "3"},
            headers={"HX-Request": "true"},
        )
        assert response.status_code == 200
        assert "<html" not in response.text
        assert "Canned." in response.text

    def test_plain_post_gets_a_whole_page(self, client):
        response = client.post(
            "/answer",
            data={"q": "wireguard", "mode": "fast", "granularity": "document", "n": "3"},
        )
        assert response.status_code == 200
        assert "<html" in response.text
        assert "Canned." in response.text

    def test_empty_query_is_refused(self, client):
        response = client.post("/answer", data={"q": "   "}, headers={"HX-Request": "true"})
        assert "Ask a question first" in response.text


class TestHealth:
    def test_healthz(self, client):
        payload = client.get("/healthz").json()
        assert payload["ok"] is True
        assert payload["notes"] >= 2

    def test_static_css_is_served(self, client):
        response = client.get("/static/app.css")
        assert response.status_code == 200
        assert "--paper" in response.text


class TestVaultSnapshot:
    def test_link_graph_refreshes_when_a_note_changes(self, client, web_vault):
        assert "Linked from" in client.get("/note/Infra/VPN.md").text
        # Remove the only inbound link; the cached graph must not serve a stale backlink.
        write(web_vault / "Infra/Hosts.md", "---\ntitle: Hosts\n---\n\nNo links now.\n")
        assert "Linked from" not in client.get("/note/Infra/VPN.md").text

    def test_new_note_becomes_readable_without_a_restart(self, client, web_vault):
        assert client.get("/note/Infra/New.md").status_code == 404
        write(web_vault / "Infra/New.md", "---\ntitle: New\n---\n\nFresh.\n")
        response = client.get("/note/Infra/New.md")
        assert response.status_code == 200
        assert "Fresh." in response.text


class TestStaleIndex:
    """`sync` rewrites Chroma's segments underneath the long-lived server.

    The open handle then queries ids that no longer exist and every search fails until
    the process restarts, so the app has to notice and rebuild on its own.
    """

    def test_reconnects_when_the_index_changes_on_disk(self, client, web_vault, tmp_path):
        app_state = client.app.state.vault
        first = app_state.store
        assert client.get("/?q=wireguard").status_code == 200

        # Re-index in a separate store, exactly as the sync agent does.
        rebuilt = IndexStore(chroma_db_path=str(tmp_path / "chroma"), provider=FakeProvider())
        write(web_vault / "Infra/Extra.md", "---\ntitle: Extra\n---\n\nA WireGuard peer.\n")
        rebuilt.sync(str(web_vault))

        response = client.get("/?q=wireguard")
        assert response.status_code == 200
        assert app_state.store is not first, "a rewritten index must be reconnected"

    def test_reconnect_actually_reopens_the_index(self, client):
        """A new IndexStore is not enough — the handle underneath it must be new too.

        `chromadb.PersistentClient` caches a System per path and hands the same rust
        bindings to every client built on it, so a rebuild that does not drop that cache
        wraps the exact stale handle it is meant to replace and recovers nothing.
        """
        app_state = client.app.state.vault
        before = app_state.store.client._system

        assert app_state.reconnect() is True
        assert app_state.store.client._system is not before

        # And the reopened index still answers.
        assert "WireGuard setup" in client.get("/?q=wireguard").text

    def test_retries_once_when_a_query_hits_a_stale_handle(self, client):
        """The sync can land mid-request, past the freshness check."""
        app_state = client.app.state.vault
        calls = []
        real = app_state.searcher.hybrid_search

        def flaky(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise ChromaInternalError("Error executing plan: Error finding id")
            return real(**kwargs)

        app_state.searcher.hybrid_search = flaky
        # Pin the signature so only the retry path can recover.
        app_state.ensure_fresh_index = lambda: None
        before = app_state.store

        response = client.get("/?q=wireguard")
        assert response.status_code == 200
        assert len(calls) == 1, "the stale handle must be hit exactly once"
        # The retry runs against the reconnected searcher, not the stale one.
        assert app_state.store is not before
        assert "WireGuard setup" in response.text

    def test_surfaces_an_error_when_reconnecting_does_not_help(self, client):
        app_state = client.app.state.vault
        app_state.ensure_fresh_index = lambda: None

        def always_stale(**kwargs):
            raise ChromaInternalError("Error executing plan: Error finding id")

        app_state.searcher.hybrid_search = always_stale
        # Reconnect installs a fresh searcher, so keep the failure in place across it.
        app_state.reconnect = lambda: True

        response = client.get("/?q=wireguard")
        assert response.status_code == 200  # the page renders; the notice carries the error
        assert "internal_error" in response.text


def test_json_routes_are_valid_json(client):
    for url in ("/healthz", "/api/retrieve?q=wireguard", "/api/note/Infra/VPN.md"):
        json.loads(client.get(url).text)
