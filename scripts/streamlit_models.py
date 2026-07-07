"""Cached providers and search resources for Streamlit pages."""

from __future__ import annotations

from typing import Optional, Tuple

import streamlit as st

from vault_rag.index.store import IndexStore
from vault_rag.llm.openrouter import OpenRouterClient
from vault_rag.retrieval.searcher import Searcher


@st.cache_resource
def get_openrouter_client() -> OpenRouterClient:
    return OpenRouterClient.from_env()


@st.cache_resource
def get_store_and_searcher() -> Tuple[Optional[IndexStore], Optional[Searcher], Optional[str]]:
    try:
        provider = get_openrouter_client()
        store = IndexStore(provider=provider)
        if store.collection.count() == 0:
            return (
                None,
                None,
                'No notes found in the index. Run `uv run vault-rag sync --root "./input/Vault 14"` first.',
            )
        searcher = Searcher(store, granularity="document", provider=provider)
        return store, searcher, None
    except Exception as exc:  # noqa: BLE001
        return None, None, f"Error initializing index: {exc}"
