"""Tests for recency-aware reranking (score-geometry strategy).

The property that matters is pool-size invariance. The previous multiplicative
strategy combined a fixed-magnitude recency factor with rank-flattened relevance
scores, whose adjacent-rank gap is 0.5 / (pool - 1); doubling the pool therefore
doubled how far freshness could move a document. The score-geometry strategy
derives its budget from the reranker's own gaps around the cutoff instead.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from vault_spider.config import SearchParams
from vault_spider.retrieval.searcher import Searcher


def _searcher() -> Searcher:
    # recency_budget is a staticmethod and calculate_freshness touches no state,
    # so a bare instance is enough here.
    return Searcher.__new__(Searcher)


def _dated(days_ago: int) -> dict:
    stamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {"updated": stamp.isoformat()}


class TestFreshness:
    def test_spans_zero_to_one(self):
        meta = {"today": _dated(0), "ancient": _dated(36500)}
        f = _searcher().calculate_freshness(["today", "ancient"], meta, 365.0)
        assert f["today"] == pytest.approx(1.0, abs=1e-3)
        assert f["ancient"] == pytest.approx(0.0, abs=1e-3)
        assert ((f >= 0.0) & (f <= 1.0)).all()

    def test_is_a_plain_negative_exponential(self):
        meta = {"a": _dated(365)}
        f = _searcher().calculate_freshness(["a"], meta, 365.0)
        # No +1.0 shift: the additive formula needs f=1 to mean "full budget"
        # and f=0 to mean "no bonus".
        assert f["a"] == pytest.approx(float(np.exp(-1.0)), abs=1e-3)

    def test_undated_notes_get_no_freshness(self):
        f = _searcher().calculate_freshness(["x"], {"x": {}}, 365.0)
        assert f["x"] == 0.0

    def test_unparseable_date_gets_no_freshness(self):
        f = _searcher().calculate_freshness(["x"], {"x": {"updated": "last Tuesday"}}, 365.0)
        assert f["x"] == 0.0

    def test_decay_days_controls_the_slope(self):
        meta = {"a": _dated(180)}
        fast = _searcher().calculate_freshness(["a"], meta, 30.0)["a"]
        slow = _searcher().calculate_freshness(["a"], meta, 3650.0)["a"]
        assert fast < slow


class TestRecencyBudget:
    def test_is_the_gap_between_cutoff_and_cutoff_plus_budget(self):
        # Ranks 1..6 with a deliberately uneven tail.
        scores = pd.Series(
            {"a": 0.913, "b": 0.910, "c": 0.907, "d": 0.905, "e": 0.903, "f": 0.901}
        )
        # k=3 -> s_(3)=0.907, B=3 -> s_(6)=0.901
        assert Searcher.recency_budget(scores, cutoff=3, rank_budget=3) == pytest.approx(
            0.006, abs=1e-9
        )

    def test_is_invariant_to_candidates_below_the_window(self):
        """The headline property: widening the pool must not change the budget."""
        base = pd.Series({"a": 0.9, "b": 0.8, "c": 0.7, "d": 0.6, "e": 0.5})
        wide = base.copy()
        for i in range(55):
            wide[f"pad{i}"] = 0.4 - i * 0.001  # 55 extra candidates, all below
        narrow_budget = Searcher.recency_budget(base, cutoff=2, rank_budget=2)
        wide_budget = Searcher.recency_budget(wide, cutoff=2, rank_budget=2)
        assert narrow_budget == pytest.approx(wide_budget)
        assert len(wide) == 60 and len(base) == 5

    def test_tracks_local_score_geometry_not_a_constant(self):
        tight = pd.Series({"a": 0.90, "b": 0.899, "c": 0.898, "d": 0.897})
        loose = pd.Series({"a": 0.90, "b": 0.70, "c": 0.50, "d": 0.30})
        # Same ranks, very different confidence gaps -> very different budgets.
        assert Searcher.recency_budget(tight, cutoff=1, rank_budget=2) < Searcher.recency_budget(
            loose, cutoff=1, rank_budget=2
        )

    def test_flat_scores_yield_no_budget(self):
        flat = pd.Series({"a": 0.5, "b": 0.5, "c": 0.5, "d": 0.5})
        assert Searcher.recency_budget(flat, cutoff=1, rank_budget=2) == 0.0

    def test_degenerate_inputs_yield_no_budget(self):
        assert Searcher.recency_budget(pd.Series(dtype=float), cutoff=5, rank_budget=3) == 0.0
        assert Searcher.recency_budget(pd.Series({"a": 1.0}), cutoff=5, rank_budget=3) == 0.0

    def test_cutoff_beyond_the_pool_clamps_without_error(self):
        scores = pd.Series({"a": 0.9, "b": 0.6, "c": 0.3})
        # cutoff already past the end: nothing below to measure against.
        assert Searcher.recency_budget(scores, cutoff=10, rank_budget=3) == 0.0
        # cutoff inside, window overruns the end: clamps to the last candidate.
        assert Searcher.recency_budget(scores, cutoff=1, rank_budget=10) == pytest.approx(0.6)

    def test_never_negative(self):
        scores = pd.Series({"a": 0.1, "b": 0.9})
        assert Searcher.recency_budget(scores, cutoff=1, rank_budget=1) >= 0.0


class TestBudgetSemantics:
    """B is a promotion allowance measured in rank positions."""

    def test_a_fresh_note_reaches_parity_b_positions_up(self):
        """B buys parity with the note B places above, so strict promotion is B-1.

        lambda_q is exactly the score spanning B positions, so a maximally fresh
        note lands level with its target rather than above it. Stable sort then
        keeps the incumbent ahead.
        """
        # Evenly spaced scores 0.01 apart, so one position costs 0.01.
        scores = pd.Series({f"n{i}": 1.0 - i * 0.01 for i in range(20)})
        budget = Searcher.recency_budget(scores, cutoff=5, rank_budget=3)
        assert budget == pytest.approx(0.03, abs=1e-9)

        # n7 sits 8th (score 0.93) and is maximally fresh; everything else stale.
        adjusted = scores.copy()
        adjusted["n7"] = adjusted["n7"] + budget
        assert adjusted["n7"] == pytest.approx(adjusted["n4"])  # parity, not victory
        ranking = list(adjusted.sort_values(ascending=False, kind="stable").index)
        assert ranking.index("n7") == 5  # from index 7, overtook n5 and n6

    def test_a_slightly_larger_budget_completes_the_bth_overtake(self):
        scores = pd.Series({f"n{i}": 1.0 - i * 0.01 for i in range(20)})
        budget = Searcher.recency_budget(scores, cutoff=5, rank_budget=3)
        adjusted = scores.copy()
        adjusted["n7"] = adjusted["n7"] + budget + 1e-6
        ranking = list(adjusted.sort_values(ascending=False, kind="stable").index)
        assert ranking.index("n7") == 4  # full B=3 promotion

    def test_freshness_cannot_overcome_a_larger_gap_than_its_budget(self):
        scores = pd.Series({"a": 0.99, "b": 0.50, "c": 0.49, "d": 0.48})
        budget = Searcher.recency_budget(scores, cutoff=2, rank_budget=2)
        # b's deficit to a is 0.49, far beyond the local tail gap.
        assert budget < 0.49
        adjusted = scores.copy()
        adjusted["b"] = adjusted["b"] + budget
        assert list(adjusted.sort_values(ascending=False, kind="stable").index)[0] == "a"


class TestSearchParamsValidation:
    def test_rejects_unknown_strategy(self):
        with pytest.raises(ValueError, match="recency_strategy"):
            SearchParams(recency_strategy="vibes")

    def test_rejects_non_positive_rank_budget(self):
        with pytest.raises(ValueError, match="recency_rank_budget"):
            SearchParams(recency_rank_budget=0)

    def test_defaults_to_score_geometry(self):
        assert SearchParams().recency_strategy == "score_geometry"
        assert SearchParams().recency_rank_budget == 1

    def test_multiplicative_remains_selectable_for_ab(self):
        assert SearchParams(recency_strategy="multiplicative").recency_strategy == (
            "multiplicative"
        )
