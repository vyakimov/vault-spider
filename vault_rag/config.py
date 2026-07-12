"""Configuration for Vault RAG retrieval and ranking."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SearchParams:
    semantic_weight: float = 0.5
    top_k: int = 150
    n_results: int = 10
    combine_strategy: str = "rrf"
    rrf_k: int = 60
    zsigmoid_temperature: float = 1.0
    rerank_top_k: int = 30
    rerank_use_ranks: bool = True
    recency_boost_enabled: bool = True
    recency_weight: float = 0.2
    recency_decay_days: float = 365.0

    def with_overrides(self, **overrides) -> "SearchParams":
        provided = {key: value for key, value in overrides.items() if value is not None}
        return replace(self, **provided)


DEFAULT_SEARCH_PARAMS = SearchParams()

BM25_CONFIG = {
    "k1": 1.2,
    "b": 0.75,
}

# Deprecated: read DEFAULT_SEARCH_PARAMS. Kept only until external readers migrate.
SEARCH_CONFIG = {
    "semantic_weight": 0.5,
    "default_top_k": 150,
    "n_results": 10,
    "combine_strategy": "rrf",
    "rrf_k": 60,
    "zsigmoid_temperature": 1.0,
    "rerank_top_k": 30,
    # (c) Treat Cohere rerank scores as ranks, not meaningful probabilities,
    # before combining with recency. Keeps ordering, discards the uncalibrated
    # magnitude so recency can't amplify score gaps that don't mean much.
    "rerank_use_ranks": True,
    "recency_boost_enabled": True,
    "recency_weight": 0.2,
    "recency_decay_days": 365.0,
}
