"""Tests for vault_ingestion: frontmatter parsing, date resolution, note loading."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from vault_ingestion import (
    build_document_text,
    coerce_datetime,
    has_ignore_tag,
    load_markdown_notes,
    normalize_tags,
    resolve_note_date,
    split_frontmatter,
)


FIXTURES = Path(__file__).parent / "fixtures" / "notes"


class TestSplitFrontmatter:
    def test_parses_yaml_frontmatter(self):
        raw = "---\ntitle: Hello\ntags: [a, b]\n---\nbody text\n"
        fm, body = split_frontmatter(raw)
        assert fm == {"title": "Hello", "tags": ["a", "b"]}
        assert body.strip() == "body text"

    def test_returns_empty_when_no_frontmatter(self):
        raw = "just body\n"
        fm, body = split_frontmatter(raw)
        assert fm == {}
        assert body == raw

    def test_returns_raw_on_invalid_yaml(self):
        raw = "---\ntitle: : :\n  bad\n---\nbody\n"
        fm, body = split_frontmatter(raw)
        assert fm == {}
        assert body == raw


class TestNormalizeTags:
    def test_list_input(self):
        assert normalize_tags(["a", "b", " c "]) == ["a", "b", "c"]

    def test_comma_separated_string(self):
        assert normalize_tags("a, b, c") == ["a", "b", "c"]

    def test_space_separated_string(self):
        assert normalize_tags("a b c") == ["a", "b", "c"]

    def test_none_returns_empty(self):
        assert normalize_tags(None) == []


class TestCoerceDatetime:
    def test_iso_string_without_tz_gets_utc(self):
        result = coerce_datetime("2024-05-01")
        assert result == dt.datetime(2024, 5, 1, tzinfo=dt.timezone.utc)

    def test_date_object(self):
        result = coerce_datetime(dt.date(2024, 5, 1))
        assert result == dt.datetime(2024, 5, 1, tzinfo=dt.timezone.utc)

    def test_invalid_string_returns_none(self):
        assert coerce_datetime("not a date") is None

    def test_none_returns_none(self):
        assert coerce_datetime(None) is None


class TestResolveNoteDate:
    def test_frontmatter_date_wins(self, tmp_path: Path):
        path = tmp_path / "whatever.md"
        path.write_text("body")
        resolved = resolve_note_date(path, {"date": "2024-05-01"})
        assert resolved.startswith("2024-05-01")

    def test_falls_back_to_filename(self, tmp_path: Path):
        path = tmp_path / "2023-09-15.md"
        path.write_text("body")
        resolved = resolve_note_date(path, {})
        assert resolved.startswith("2023-09-15")

    def test_falls_back_to_mtime(self, tmp_path: Path):
        path = tmp_path / "untitled.md"
        path.write_text("body")
        resolved = resolve_note_date(path, {})
        # Parseable ISO timestamp with tz info.
        parsed = dt.datetime.fromisoformat(resolved)
        assert parsed.tzinfo is not None


class TestHasIgnoreTag:
    def test_detects_ignore_tag(self):
        assert has_ignore_tag("some text #ignore more text")

    def test_detects_secret_tag(self):
        assert has_ignore_tag("#secret stuff")

    def test_case_insensitive(self):
        assert has_ignore_tag("#Ignore")

    def test_plain_word_not_matched(self):
        assert not has_ignore_tag("please ignore this")

    def test_subtag_not_matched(self):
        assert not has_ignore_tag("#ignored-for-now")


class TestBuildDocumentText:
    def test_includes_title_path_tags_date_body(self):
        text = build_document_text(
            "Title", "folder/note.md", ["a", "b"], "2024-01-01T00:00:00+00:00", "hello"
        )
        assert "# Title" in text
        assert "Path: folder/note.md" in text
        assert "Tags: a, b" in text
        assert "Date: 2024-01-01" in text
        assert "hello" in text

    def test_omits_tags_when_empty(self):
        text = build_document_text("T", "p.md", [], "", "body")
        assert "Tags:" not in text


class TestLoadMarkdownNotes:
    def test_loads_all_fixture_notes(self):
        notes = load_markdown_notes(str(FIXTURES))
        assert len(notes) == 20

    def test_each_note_has_required_metadata(self):
        notes = load_markdown_notes(str(FIXTURES))
        for note in notes:
            md = note["metadata"]
            assert md["title"]
            assert md["path"].endswith(".md")
            assert md["source"] == "vault_markdown"
            # Date resolves to an ISO string we can parse back.
            dt.datetime.fromisoformat(md["date"])

    def test_ids_are_unique(self):
        notes = load_markdown_notes(str(FIXTURES))
        ids = [note["id"] for note in notes]
        assert len(ids) == len(set(ids))

    def test_documents_contain_body(self):
        notes = load_markdown_notes(str(FIXTURES))
        sourdough = next(n for n in notes if "sourdough" in n["metadata"]["path"])
        assert "starter" in sourdough["document"].lower()

    def test_missing_vault_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_markdown_notes(str(tmp_path / "does-not-exist"))
