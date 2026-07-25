"""Tests for vault_spider.corpus.vault (single-note and whole-vault reads)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vault_spider.corpus.vault import load_vault_notes, read_note


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def vault(tmp_path):
    write(tmp_path / "A.md", "---\ntitle: Alpha\ntags:\n  - infra\naliases:\n  - Al\n---\nBody A.\n")
    write(tmp_path / "Folder/B.md", "Body B with [[A]].\n")
    write(tmp_path / "secret.md", "---\ntags:\n  - secret\n---\nClassified.\n")
    write(tmp_path / "inline_secret.md", "Nothing to see #ignore here.\n")
    write(tmp_path / "Templates/T.md", "A template.\n")
    write(tmp_path / ".obsidian/config.md", "Not a note.\n")
    write(tmp_path / "Excalidraw/map.excalidraw.md", "---\nexcalidraw-plugin: parsed\n---\ndraw\n")
    return tmp_path


class TestReadNote:
    def test_reads_frontmatter_and_body(self, vault):
        note = read_note(str(vault), "A.md")
        assert note is not None
        assert note.title == "Alpha"
        assert note.stem == "A"
        assert note.body.strip() == "Body A."
        assert note.tags == ["infra"]
        assert note.aliases == ["Al"]
        assert note.frontmatter_text == "title: Alpha\ntags:\n  - infra\naliases:\n  - Al"

    def test_title_falls_back_to_stem(self, vault):
        note = read_note(str(vault), "Folder/B.md")
        assert note is not None and note.title == "B"

    def test_missing_note_is_none(self, vault):
        assert read_note(str(vault), "Nope.md") is None

    def test_directory_is_none(self, vault):
        assert read_note(str(vault), "Folder") is None

    def test_non_markdown_is_none(self, vault):
        write(vault / "notes.txt", "hello")
        assert read_note(str(vault), "notes.txt") is None

    @pytest.mark.parametrize(
        "path",
        ["../outside.md", "/etc/passwd", "a/../../b.md", "", "a\\b.md"],
    )
    def test_unsafe_paths_are_rejected(self, vault, path):
        with pytest.raises(ValueError):
            read_note(str(vault), path)

    def test_symlink_escaping_the_vault_is_none(self, vault, tmp_path):
        outside = tmp_path.parent / "outside_secret.md"
        outside.write_text("secrets\n", encoding="utf-8")
        (vault / "escape.md").symlink_to(outside)
        assert read_note(str(vault), "escape.md") is None

    def test_ignored_notes_are_indistinguishable_from_missing(self, vault):
        """A `#secret` note must not be readable through this module."""
        assert read_note(str(vault), "secret.md") is None
        assert read_note(str(vault), "inline_secret.md") is None

    def test_skipped_directories_are_none(self, vault):
        assert read_note(str(vault), "Templates/T.md") is None
        assert read_note(str(vault), ".obsidian/config.md") is None

    def test_excalidraw_is_none(self, vault):
        assert read_note(str(vault), "Excalidraw/map.excalidraw.md") is None


class TestLoadVaultNotes:
    def test_loads_readable_notes_and_counts_ignored(self, vault):
        notes, ignored = load_vault_notes(str(vault))
        assert sorted(note.path for note in notes) == ["A.md", "Folder/B.md"]
        # secret.md, inline_secret.md and the Excalidraw drawing are skipped by policy;
        # Templates/ and .obsidian/ are not walked at all.
        assert ignored == 3

    def test_notes_satisfy_the_link_node_protocol(self, vault):
        from vault_spider.corpus.links import build_link_graph

        notes, _ = load_vault_notes(str(vault))
        graph = build_link_graph(notes)
        assert graph.links_to("A.md") == ["Folder/B.md"]
