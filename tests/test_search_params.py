from dataclasses import fields

from vault_rag.config import DEFAULT_SEARCH_PARAMS, SEARCH_CONFIG, SearchParams


def test_with_overrides_ignores_none_and_applies_values():
    params = SearchParams().with_overrides(n_results=4, semantic_weight=None)

    assert params.n_results == 4
    assert params.semantic_weight == 0.5


def test_default_search_params_match_legacy_config():
    for field in fields(SearchParams):
        config_key = "default_top_k" if field.name == "top_k" else field.name
        if config_key in SEARCH_CONFIG:
            assert getattr(DEFAULT_SEARCH_PARAMS, field.name) == SEARCH_CONFIG[config_key]
