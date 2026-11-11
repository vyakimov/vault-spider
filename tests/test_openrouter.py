"""Tests for vault_spider.llm.openrouter request/response hardening (no network)."""

from __future__ import annotations

import httpx
import pytest

from vault_spider.llm import openrouter
from vault_spider.llm.openrouter import OpenRouterClient, OpenRouterError


def make_client() -> OpenRouterClient:
    return OpenRouterClient(api_key="key", embedding_model="e", chat_model="c")


def test_missing_api_key_raises():
    with pytest.raises(ValueError):
        OpenRouterClient(api_key="", embedding_model="e", chat_model="c")


def test_post_raises_on_non_json_body(monkeypatch):
    client = make_client()
    monkeypatch.setattr(
        httpx, "post", lambda *args, **kwargs: httpx.Response(200, text="<html>oops</html>")
    )
    with pytest.raises(OpenRouterError, match="non-JSON"):
        client._post("/embeddings", {})


def test_post_rejects_non_object_json(monkeypatch):
    client = make_client()
    monkeypatch.setattr(
        httpx, "post", lambda *args, **kwargs: httpx.Response(200, json=[])
    )
    with pytest.raises(OpenRouterError, match="not an object"):
        client._post("/embeddings", {})


def test_post_surfaces_body_after_retryable_statuses_exhaust(monkeypatch):
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return httpx.Response(502, text="bad gateway")

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(openrouter.time, "sleep", lambda seconds: None)

    client = make_client()
    with pytest.raises(OpenRouterError, match="bad gateway"):
        client._post("/embeddings", {}, retries=3)
    assert calls["n"] == 3


def test_post_raises_immediately_on_non_retryable_status(monkeypatch):
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return httpx.Response(401, text="unauthorized")

    monkeypatch.setattr(httpx, "post", fake_post)

    client = make_client()
    with pytest.raises(OpenRouterError, match="unauthorized"):
        client._post("/chat/completions", {})
    assert calls["n"] == 1


def test_embed_texts_rejects_partial_batches(monkeypatch):
    client = make_client()
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, payload: {"data": [{"index": 0, "embedding": [1.0, 0.0]}]},
    )
    with pytest.raises(OpenRouterError, match="2 inputs"):
        client.embed_texts(["first", "second"])


def test_embed_texts_rejects_duplicate_indices(monkeypatch):
    client = make_client()
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, payload: {
            "data": [
                {"index": 0, "embedding": [1.0, 0.0]},
                {"index": 0, "embedding": [0.0, 1.0]},
            ]
        },
    )
    with pytest.raises(OpenRouterError, match="duplicate index 0"):
        client.embed_texts(["first", "second"])


def test_embed_texts_rejects_inconsistent_dimensions(monkeypatch):
    client = make_client()
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, payload: {
            "data": [
                {"index": 0, "embedding": [1.0, 0.0]},
                {"index": 1, "embedding": [0.0, 1.0, 0.0]},
            ]
        },
    )
    with pytest.raises(OpenRouterError, match="dimensions were inconsistent"):
        client.embed_texts(["first", "second"])


def test_rerank_rejects_negative_index(monkeypatch):
    client = OpenRouterClient(
        api_key="key", embedding_model="e", chat_model="c", rerank_model="r"
    )
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, payload: {"results": [{"index": -1, "relevance_score": 0.9}]},
    )
    with pytest.raises(OpenRouterError, match="invalid index -1"):
        client.rerank("query", ["document"], ["id"])


def _capture_chat_payload(monkeypatch, client):
    captured = {}

    def fake_post(path, payload):
        captured["payload"] = payload
        return {"choices": [{"message": {"content": "{}"}}]}

    monkeypatch.setattr(client, "_post", fake_post)
    client.chat("system", "user")
    return captured["payload"]


def test_chat_omits_drop_params_by_default(monkeypatch):
    payload = _capture_chat_payload(monkeypatch, make_client())
    assert "drop_params" not in payload


def test_chat_sends_drop_params_when_enabled(monkeypatch):
    client = OpenRouterClient(
        api_key="key", embedding_model="e", chat_model="c", drop_params=True
    )
    assert _capture_chat_payload(monkeypatch, client)["drop_params"] is True


@pytest.mark.parametrize(
    "value,expected", [("true", True), ("1", True), ("", True), ("no", False), ("false", False)]
)
def test_from_env_reads_drop_params_flag(monkeypatch, value, expected):
    monkeypatch.setenv("MARKETPLACE_API_KEY", "key")
    monkeypatch.setenv("MARKETPLACE_DROP_PARAMS", value)
    assert OpenRouterClient.from_env().drop_params is expected


def test_from_env_defaults_to_marketplace(monkeypatch):
    for name in (
        "MARKETPLACE_BASE_URL",
        "MARKETPLACE_EMBEDDING_MODEL",
        "MARKETPLACE_CHAT_MODEL",
        "MARKETPLACE_DROP_PARAMS",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("MARKETPLACE_API_KEY", "key")
    client = OpenRouterClient.from_env()
    assert client.base_url == openrouter.DEFAULT_BASE_URL
    assert client.embedding_model == openrouter.DEFAULT_EMBEDDING_MODEL
    assert client.chat_model == openrouter.DEFAULT_CHAT_MODEL
    assert client.drop_params is True
