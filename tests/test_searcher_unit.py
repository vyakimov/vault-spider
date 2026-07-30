import math
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from tests.conftest import EMBED_DIM, FakeProvider
from vault_spider.config import DEFAULT_SEARCH_PARAMS
from vault_spider.index.store import IndexStore
from vault_spider.llm.openrouter import OpenRouterError
from vault_spider.retrieval import searcher as searcher_module
from vault_spider.retrieval.searcher import (
    GRAPH_DECAY,
    GRAPH_NEIGHBOR_CAP,
    GRAPH_WEIGHT,
    Searcher,
)
from vault_spider.utils import tokenize_for_bm25


def test_unquoted_keyword_scores_match_bm25(tmp_path, tiny_vault, fake_provider):
    store = IndexStore(str(tmp_path / "chroma"), provider=fake_provider)
    store.sync(str(tiny_vault))
    documents, ids, _, bm25 = store.granularity_data("document")
    searcher = Searcher(store, provider=fake_provider)

    actual = searcher.calculate_keyword_scores("alpha notes", ids, documents, bm25)
    tokens = tokenize_for_bm25("alpha notes", searcher.stop_words, searcher.stemmer)
    expected = pd.Series(dict(zip(ids, bm25.get_scores(tokens))), dtype=float)

    pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_quoted_phrase_applies_boost(tmp_path, tiny_vault, fake_provider):
    store = IndexStore(str(tmp_path / "chroma"), provider=fake_provider)
    store.sync(str(tiny_vault))
    documents, ids, _, bm25 = store.granularity_data("document")
    searcher = Searcher(store, provider=fake_provider)

    actual = searcher.calculate_keyword_scores('"zqxq"', ids, documents, bm25)
    tokens = tokenize_for_bm25('"zqxq"', searcher.stop_words, searcher.stemmer)
    base = dict(zip(ids, bm25.get_scores(tokens)))
    big_id = next(doc_id for doc_id, document in zip(ids, documents) if "zqxq" in document)

    assert actual[big_id] == float(base[big_id]) * 1.3


# -- graph expansion ---------------------------------------------------------
#
# The failure mode these guard against is shipping the feature *inert*. Expansion
# that only reshuffles the rerank pool changes no output, because `relevance_score`
# is overwritten by the reranker afterwards. So the load-bearing assertions are
# "a linked note the query cannot reach surfaces" and "the bonus reaches `final`".


class KeywordProvider(FakeProvider):
    """Embeds on a keyword rather than a hash, so semantic ranking is controlled."""

    MARKER = "wireguard"

    def embed_texts(self, texts, batch_size=32):
        self.embed_calls.append(list(texts))
        return [self._axis(text) for text in texts]

    def _axis(self, text: str):
        vector = [0.0] * EMBED_DIM
        vector[0 if self.MARKER in text.lower() else 1] = 1.0
        return vector


HUB_ID = "01JGRAPH00000000000000HUB0"
LEAF_ID = "01JGRAPH00000000000000LEAF"
QUERY = "wireguard tunnel handshake"


@pytest.fixture
def linked_vault(tmp_path: Path) -> Path:
    """A hub the query hits, and a leaf reachable only through the hub's wikilink."""
    vault = tmp_path / "linked-vault"
    vault.mkdir()
    (vault / "hub.md").write_text(
        f"---\nid: {HUB_ID}\ntitle: Hub\n---\n"
        "Wireguard tunnel handshake overview for the site link.\n\n"
        "See [[leaf]] for the rest.\n",
        encoding="utf-8",
    )
    # No query term, and the opposite embedding axis: unreachable except via the link.
    (vault / "leaf.md").write_text(
        f"---\nid: {LEAF_ID}\ntitle: Leaf\n---\n"
        "Quarterly budget spreadsheet totals and stationery receipts.\n",
        encoding="utf-8",
    )
    # Comfortably more than GRAPH_SEED_COUNT: with a corpus smaller than the seed
    # count every note is a seed, and seeds are excluded from their own neighbours.
    for index in range(14):
        (vault / f"filler_{index:02d}.md").write_text(
            f"---\nid: 01JGRAPH000000000000FIL{index:02d}\ntitle: Filler {index}\n---\n"
            "Wireguard tunnel handshake filler note about the same subject.\n",
            encoding="utf-8",
        )
    return vault


@pytest.fixture
def small_pool(monkeypatch):
    """Shrink the rerank pool so admission actually bites in a tiny corpus."""
    monkeypatch.setattr(
        searcher_module,
        "DEFAULT_SEARCH_PARAMS",
        replace(DEFAULT_SEARCH_PARAMS, rerank_top_k=2),
    )


def _build(tmp_path, vault, provider):
    store = IndexStore(str(tmp_path / "chroma"), provider=provider)
    store.sync(str(vault))
    return store, Searcher(store, provider=provider)


def _search(searcher, **overrides):
    """Recency off so `final` is the relevance score, and no truncation at n=10."""
    kwargs = {
        "mode": "thorough",
        "granularity": "document",
        "n_results": 30,
        "recency_boost_enabled": False,
    }
    kwargs.update(overrides)
    return searcher.hybrid_search(QUERY, **kwargs)


def _leaf_row(result):
    return next((row for row in result.rows if row["note_id"] == LEAF_ID), None)


def test_graph_expansion_surfaces_a_note_the_query_cannot_reach(
    tmp_path, linked_vault, small_pool
):
    store, searcher = _build(tmp_path, linked_vault, KeywordProvider())
    assert store.graph_status == "ok"

    result = _search(searcher)

    leaf = _leaf_row(result)
    assert leaf is not None, "the linked leaf never surfaced"
    assert leaf["graph"]["seed_note_id"] == HUB_ID
    assert leaf["graph"]["seed_path"] == "hub.md"
    assert leaf["graph"]["hop_count"] == 1
    assert leaf["graph"]["propagated_score"] > 0.0
    assert result.debug_info["graph"]["applied"] is True
    assert result.debug_info["graph"]["entries_in_rerank_pool"] >= 1


def test_fast_mode_never_expands(tmp_path, linked_vault, small_pool):
    _, searcher = _build(tmp_path, linked_vault, KeywordProvider())

    result = _search(searcher, mode="fast")

    assert result.debug_info["graph"]["eligible"] is False
    assert all(row["graph"] is None for row in result.rows)


def test_no_expansion_without_a_reranker(tmp_path, linked_vault, small_pool):
    _, searcher = _build(tmp_path, linked_vault, KeywordProvider(rerank_model=None))

    result = _search(searcher)

    assert result.debug_info["graph"]["eligible"] is False
    assert all(row["graph"] is None for row in result.rows)


def test_no_expansion_when_the_graph_is_stale(tmp_path, linked_vault, small_pool):
    store, searcher = _build(tmp_path, linked_vault, KeywordProvider())
    store.graph_status = "stale"

    result = _search(searcher)

    assert result.debug_info["graph"]["eligible"] is False
    assert result.debug_info["graph"]["status"] == "stale"
    assert all(row["graph"] is None for row in result.rows)


def test_expansion_cannot_route_a_candidate_around_a_filter(
    tmp_path, linked_vault, small_pool
):
    """The leaf is a genuine neighbour, but it fails the required-term filter."""
    _, searcher = _build(tmp_path, linked_vault, KeywordProvider())

    result = _search(searcher, must_include_terms=["wireguard"])

    assert _leaf_row(result) is None
    assert all(row["graph"] is None for row in result.rows)


def test_rerank_failure_discards_graph_results(tmp_path, linked_vault, small_pool):
    provider = KeywordProvider()
    _, searcher = _build(tmp_path, linked_vault, provider)

    def _boom(**kwargs):
        raise OpenRouterError("rerank unavailable")

    provider.rerank = _boom

    result = _search(searcher)

    assert result.debug_info["graph"]["applied"] is False
    assert result.debug_info["graph"]["fallback_reason"] == "rerank_unavailable"
    assert all(row["graph"] is None for row in result.rows)


def test_the_bonus_reaches_the_final_score(
    tmp_path, linked_vault, small_pool, monkeypatch
):
    """Without this the feature is inert: pool-only expansion changes no output."""
    _, searcher = _build(tmp_path, linked_vault, KeywordProvider())

    with_bonus = _leaf_row(_search(searcher))
    monkeypatch.setattr(searcher_module, "GRAPH_WEIGHT", 0.0)
    without_bonus = _leaf_row(_search(searcher))

    assert with_bonus is not None and without_bonus is not None
    # GRAPH_WEIGHT is denominated in rank-derived relevance, which spans [0.5, 1.0].
    # score_geometry recency ranks on the reranker's raw scores instead, so the bonus
    # is rescaled into whatever spread this query actually produced. Reconstructing
    # that factor keeps the assertion exact rather than approximate.
    spread = with_bonus["_relevance_spread"]
    scale = (spread / 0.5) if spread else 1.0
    expected = without_bonus["final"] + GRAPH_WEIGHT * scale * with_bonus["graph"][
        "propagated_score"
    ]
    assert with_bonus["final"] == pytest.approx(expected)
    assert with_bonus["final"] > without_bonus["final"]


def test_damping_and_caps_are_deterministic():
    """A hub must be damped by its degree, and the neighbour cap must bite."""

    class StubStore:
        graph_status = "ok"

        def __init__(self, adjacency):
            self.adjacency = adjacency

        def graph_neighbors(self, note_id):
            return set(self.adjacency.get(note_id, set()))

        def graph_degree(self, note_id):
            return len(self.adjacency.get(note_id, set()))

    hub_neighbors = {f"n{index:03d}" for index in range(40)}
    adjacency = {"seed": hub_neighbors}
    adjacency.update({name: {"seed"} for name in hub_neighbors})
    searcher = Searcher.__new__(Searcher)
    searcher.store = StubStore(adjacency)

    reached = searcher._graph_neighbors(["seed"], {"seed": 1.0})

    assert len(reached) == GRAPH_NEIGHBOR_CAP
    # seed degree 40, neighbour degree 1 -> sqrt(ln 42 * ln 3) damping.
    expected = GRAPH_DECAY / math.sqrt(math.log(42) * math.log(3))
    assert all(score == pytest.approx(expected) for score, _ in reached.values())
    # Every score ties, so the cap must fall on sorted note ids, not set order.
    assert sorted(reached) == sorted(hub_neighbors)[:GRAPH_NEIGHBOR_CAP]
