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


_PROVIDER_ENV = [
    "LLM_PROVIDER",
    *(
        prefix + name
        for prefix in ("MARKETPLACE_", "OPENROUTER_")
        for name in (
            "API_KEY", "BASE_URL", "EMBEDDING_MODEL", "CHAT_MODEL", "RERANK_MODEL",
            "CONTEXT_MODEL", "HTTP_REFERER", "APP_TITLE", "DROP_PARAMS",
        )
    ),
]


@pytest.fixture
def clean_env(monkeypatch):
    """Drop provider variables that load_dotenv() copied from this machine's .env."""
    for name in _PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.mark.parametrize(
    "value,expected", [("true", True), ("1", True), ("", True), ("no", False), ("false", False)]
)
def test_from_env_reads_drop_params_flag(clean_env, value, expected):
    clean_env.setenv("MARKETPLACE_API_KEY", "key")
    clean_env.setenv("MARKETPLACE_DROP_PARAMS", value)
    assert OpenRouterClient.from_env().drop_params is expected


def test_from_env_defaults_to_marketplace(clean_env):
    clean_env.setenv("MARKETPLACE_API_KEY", "key")
    client = OpenRouterClient.from_env()
    assert client.base_url == openrouter.DEFAULT_BASE_URL
    assert client.embedding_model == openrouter.DEFAULT_EMBEDDING_MODEL
    assert client.chat_model == openrouter.DEFAULT_CHAT_MODEL
    assert client.drop_params is True


def test_from_env_uses_openrouter_when_only_its_key_is_set(clean_env):
    clean_env.setenv("OPENROUTER_API_KEY", "or-key")
    clean_env.setenv("OPENROUTER_EMBEDDING_MODEL", "google/gemini-embedding-2")
    client = OpenRouterClient.from_env()
    assert client.api_key == "or-key"
    assert client.base_url == "https://openrouter.ai/api/v1"
    assert client.embedding_model == "google/gemini-embedding-2"
    assert client.chat_model == "openai/gpt-4o-mini"
    assert client.drop_params is False


def test_from_env_ignores_the_other_providers_variables(clean_env):
    clean_env.setenv("OPENROUTER_API_KEY", "or-key")
    clean_env.setenv("MARKETPLACE_EMBEDDING_MODEL", "gemini_embedding_2")
    client = OpenRouterClient.from_env()
    assert client.embedding_model == "openai/text-embedding-3-small"


def test_from_env_requires_a_key(clean_env):
    with pytest.raises(ValueError, match="MARKETPLACE_API_KEY or OPENROUTER_API_KEY"):
        OpenRouterClient.from_env()


def test_from_env_refuses_two_keys_without_llm_provider(clean_env):
    clean_env.setenv("MARKETPLACE_API_KEY", "mk")
    clean_env.setenv("OPENROUTER_API_KEY", "or")
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        OpenRouterClient.from_env()


def test_llm_provider_picks_between_two_keys(clean_env):
    clean_env.setenv("MARKETPLACE_API_KEY", "mk")
    clean_env.setenv("OPENROUTER_API_KEY", "or")
    clean_env.setenv("LLM_PROVIDER", "OpenRouter")
    assert OpenRouterClient.from_env().api_key == "or"


def test_llm_provider_rejects_unknown_names(clean_env):
    clean_env.setenv("LLM_PROVIDER", "anthropic")
    with pytest.raises(ValueError, match="LLM_PROVIDER must be one of"):
        OpenRouterClient.from_env()
