"""Tests for vault_spider.web.format — retrieval contracts turned into readable things."""

from __future__ import annotations

import pytest

from vault_spider.web.format import (
    candidate_url,
    clean_excerpt,
    decorate_candidates,
    humanize_error,
    link_citations,
    preview,
    short_date,
)
from vault_spider.web.markdown import render_inline

# What `chunker.document_text()` actually produces.
INDEXED = (
    "# WireGuard setup\n\nPath: Infra/VPN.md\n\nTags: infra, vpn\n\n"
    "Date: 2026-01-15T10:00:00+01:00\n\nThe real body starts here.\n"
)
INDEXED_SECTION = "# WireGuard setup\n\nSection: Key rotation\n\nRotate every 90 days.\n"


def candidate(**overrides):
    base = {
        "note_id": "n1",
        "path": "Infra/VPN.md",
        "title": "WireGuard setup",
        "heading": "",
        "line_start": 0,
        "line_end": 0,
        "excerpt": INDEXED,
        "why": "strong keyword match",
        "scores": {"bm25": 1.0, "semantic": 1.0, "fused": 1.0, "reranker": None, "final": 1.0},
    }
    base.update(overrides)
    return base


class TestCleanExcerpt:
    def test_strips_the_synthesized_document_header(self):
        assert clean_excerpt(INDEXED) == "The real body starts here."

    def test_strips_the_section_header(self):
        assert clean_excerpt(INDEXED_SECTION) == "Rotate every 90 days."

    def test_leaves_a_plain_body_alone(self):
        assert clean_excerpt("Just prose.") == "Just prose."

    def test_handles_empty(self):
        assert clean_excerpt("") == ""


class TestPreview:
    def test_wikilinks_become_plain_text(self):
        assert preview("See [[Target]] now.") == "See Target now."

    def test_alias_wins(self):
        assert preview("See [[Target|the guide]].") == "See the guide."

    def test_heading_link_shows_the_target(self):
        assert preview("See [[Target#Section]].") == "See Target."

    def test_markdown_noise_is_removed(self):
        assert preview("## Head\n\n**bold** and `code` and ==mark==") == (
            "Head bold and code and mark"
        )

    def test_callout_markers_are_removed(self):
        assert preview("> [!NOTE] Heads up\n> The body.") == "Heads up The body."

    def test_list_bullets_are_removed(self):
        assert preview("- one\n- two\n- [ ] three") == "one two three"

    def test_links_keep_their_text(self):
        assert preview("A [link](https://example.com) here.") == "A link here."

    def test_a_repeated_title_is_dropped(self):
        assert preview("# Alpha\n\nAlpha is a thing.", title="Alpha") == "is a thing."

    def test_a_different_opening_is_kept(self):
        assert preview("Beta is a thing.", title="Alpha") == "Beta is a thing."

    def test_collapses_to_one_line(self):
        assert "\n" not in preview("a\n\n\nb\n\nc")


class TestCandidateUrl:
    def test_plain_note(self):
        assert candidate_url(candidate()) == "/note/Infra/VPN.md"

    def test_carries_the_range_and_anchor(self):
        url = candidate_url(candidate(line_start=4, line_end=30))
        assert url == "/note/Infra/VPN.md?from=4&to=30#L4"

    def test_carries_the_query(self):
        url = candidate_url(candidate(), query="vpn setup")
        assert url == "/note/Infra/VPN.md?q=vpn+setup"

    def test_encodes_spaces_in_the_path(self):
        url = candidate_url(candidate(path="200 Tech/My Note.md"))
        assert url == "/note/200%20Tech/My%20Note.md"


class TestEvidenceBar:
    def test_the_stronger_signal_leads(self):
        rows = decorate_candidates([
            candidate(scores={"bm25": 10.0, "semantic": 1.0, "fused": 1, "reranker": None,
                              "final": 1}),
            candidate(scores={"bm25": 1.0, "semantic": 10.0, "fused": 1, "reranker": None,
                              "final": 1}),
        ])
        assert rows[0]["bar"]["lead"] == "keyword"
        assert rows[0]["bar"]["keyword"] == 100
        assert rows[1]["bar"]["lead"] == "semantic"
        assert rows[1]["bar"]["semantic"] == 100

    def test_identical_scores_do_not_divide_by_zero(self):
        rows = decorate_candidates([candidate(), candidate()])
        assert all(0 <= row["bar"]["keyword"] <= 100 for row in rows)

    def test_rerank_is_flagged(self):
        scores = {"bm25": 1.0, "semantic": 1.0, "fused": 1.0, "reranker": 0.9, "final": 1.0}
        assert decorate_candidates([candidate(scores=scores)])[0]["bar"]["reranked"] is True
        assert decorate_candidates([candidate()])[0]["bar"]["reranked"] is False

    def test_empty_candidate_list(self):
        assert decorate_candidates([]) == []

    def test_positions_start_at_one(self):
        rows = decorate_candidates([candidate(), candidate()])
        assert [row["position"] for row in rows] == [1, 2]


class TestCitations:
    def test_markers_become_links(self):
        answer = "The tunnel is up [S0]."
        citations = [{"key": "S0", "path": "Infra/VPN.md"}]
        assert link_citations(answer, citations) == (
            "The tunnel is up [[S0](/note/Infra/VPN.md)]."
        )

    def test_paths_with_spaces_are_encoded_so_the_link_parses(self):
        """A raw space in a Markdown destination stops it being a link at all."""
        result = link_citations("See [S0].", [{"key": "S0", "path": "200 Tech/My Note.md"}])
        assert result == "See [[S0](/note/200%20Tech/My%20Note.md)]."
        assert 'href="/note/200%20Tech/My%20Note.md"' in render_inline(result)

    def test_multiple_keys_in_one_marker(self):
        citations = [{"key": "S0", "path": "a.md"}, {"key": "S1", "path": "b.md"}]
        result = link_citations("Both [S0, S1] agree.", citations)
        assert "/note/a.md" in result and "/note/b.md" in result

    def test_unknown_key_is_left_as_text(self):
        assert link_citations("See [S9].", []) == "See [S9]."

    def test_empty_answer(self):
        assert link_citations("", []) == ""


class TestMisc:
    @pytest.mark.parametrize(
        "value,expected",
        [("2026-01-15T10:00:00Z", "15 Jan 2026"), ("", ""), (None, ""), ("nonsense", "nonsense")],
    )
    def test_short_date(self, value, expected):
        assert short_date(value) == expected

    def test_humanize_error_adds_guidance(self):
        result = humanize_error("index_empty", "index is empty")
        assert result["type"] == "index_empty"
        assert "sync" in result["guidance"]

    def test_unknown_error_type_has_no_guidance(self):
        assert humanize_error("weird", "x")["guidance"] == ""
