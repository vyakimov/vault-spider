"""Tests for vault_spider.corpus.links."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from vault_spider.corpus.links import (
    WIKILINK_TOKEN_RE,
    Resolver,
    build_link_graph,
    extract_frontmatter_wikilinks,
    extract_wikilinks,
    parse_wikilink,
)


@dataclass
class FakeNote:
    """The minimal shape satisfying the LinkNode protocol."""

    path: str
    body: str = ""
    frontmatter_text: str = ""
    title: str = ""
    aliases: List[str] = field(default_factory=list)

    @property
    def stem(self) -> str:  # type: ignore[override]
        return self.path.rsplit("/", 1)[-1].removesuffix(".md")

    def __post_init__(self):
        if not self.title:
            self.title = self.stem


class TestExtractWikilinks:
    def test_alias_and_heading_links(self):
        links = extract_wikilinks("See [[Target|shown]] and [[Other#Section]].")
        targets = [t for t, _ in links]
        assert targets == ["Target", "Other"]

    def test_ignores_fenced_and_backtick(self):
        body = "Real [[Here]].\n```\n[[InFence]]\n```\n`[[InCode]]`\n"
        targets = [t for t, _ in extract_wikilinks(body)]
        assert targets == ["Here"]

    def test_line_numbers(self):
        body = "line1\n[[Two]]\n"
        assert extract_wikilinks(body) == [("Two", 2)]


class TestExtractFrontmatterWikilinks:
    def test_reads_links_from_values(self):
        block = 'parents: "[[Daily Notes]]"\ntags:\n  - x\n'
        assert extract_frontmatter_wikilinks(block) == [("Daily Notes", 2)]

    def test_no_links_is_empty(self):
        assert extract_frontmatter_wikilinks("tags:\n  - x\n") == []


class TestParseWikilink:
    def parse(self, text: str):
        match = WIKILINK_TOKEN_RE.search(text)
        assert match is not None
        return parse_wikilink(match)

    def test_plain_link(self):
        link = self.parse("[[Target]]")
        assert (link.target, link.heading, link.alias, link.is_embed) == ("Target", "", "", False)
        assert link.display == "Target"

    def test_alias_wins_over_target(self):
        assert self.parse("[[Target|Shown]]").display == "Shown"

    def test_heading_is_captured_and_shown(self):
        link = self.parse("[[Target#Section]]")
        assert (link.target, link.heading) == ("Target", "Section")
        assert link.display == "Target › Section"

    def test_embed_is_flagged(self):
        assert self.parse("![[diagram.png]]").is_embed is True

    def test_same_note_heading_link(self):
        link = self.parse("[[#Section]]")
        assert (link.target, link.heading) == ("", "Section")
        assert link.display == "Section"

    def test_alias_with_heading(self):
        link = self.parse("[[Target#Section|Shown]]")
        assert (link.target, link.heading, link.alias) == ("Target", "Section", "Shown")
        assert link.display == "Shown"


class TestResolver:
    def test_resolves_by_stem_title_path_and_alias(self):
        notes = [
            FakeNote(path="Folder/Note A.md", title="Alpha", aliases=["A-alias"]),
        ]
        resolver = Resolver(notes)
        assert resolver.resolve("Note A") == "Folder/Note A.md"
        assert resolver.resolve("Alpha") == "Folder/Note A.md"
        assert resolver.resolve("Folder/Note A") == "Folder/Note A.md"
        assert resolver.resolve("Folder/Note A.md") == "Folder/Note A.md"
        assert resolver.resolve("a-alias") == "Folder/Note A.md"
        assert resolver.resolve("Nope") is None

    def test_attachments_resolve_by_name_or_path(self):
        resolver = Resolver([], ["!attachments/diagram.png"])
        assert resolver.resolve_attachment("diagram.png") == "!attachments/diagram.png"
        assert resolver.resolve_attachment("!attachments/diagram.png") == (
            "!attachments/diagram.png"
        )
        assert resolver.resolve("diagram.png") is None  # not a note

    def test_excalidraw_resolves_without_md_suffix(self):
        resolver = Resolver([], ["Excalidraw/map0.excalidraw.md"])
        assert resolver.resolve_attachment("map0.excalidraw") == "Excalidraw/map0.excalidraw.md"


class TestBuildLinkGraph:
    def test_edges_and_backlinks(self):
        notes = [
            FakeNote(path="A.md", body="Links to [[B]] and [[C]].\n"),
            FakeNote(path="B.md", body="Back to [[A]].\n"),
            FakeNote(path="C.md"),
        ]
        graph = build_link_graph(notes)
        assert graph.links_from("A.md") == ["B.md", "C.md"]
        assert graph.links_to("A.md") == ["B.md"]
        assert graph.links_to("C.md") == ["A.md"]
        assert graph.links_from("C.md") == []

    def test_frontmatter_links_are_edges(self):
        notes = [
            FakeNote(path="A.md", frontmatter_text='parents: "[[B]]"'),
            FakeNote(path="B.md"),
        ]
        graph = build_link_graph(notes)
        assert graph.links_from("A.md") == ["B.md"]
        assert graph.links_to("B.md") == ["A.md"]

    def test_self_links_are_neither_edges_nor_unresolved(self):
        graph = build_link_graph([FakeNote(path="A.md", body="See [[A]].\n")])
        assert graph.links_from("A.md") == []
        assert graph.unresolved == []

    def test_unresolved_links_are_reported_in_order(self):
        notes = [
            FakeNote(path="A.md", body="Nope [[Missing]].\n", frontmatter_text='up: "[[Gone]]"'),
        ]
        graph = build_link_graph(notes)
        assert [(u.target, u.line, u.location) for u in graph.unresolved] == [
            ("Missing", 1, "body"),
            ("Gone", 2, "frontmatter"),
        ]

    def test_attachment_links_are_not_unresolved(self):
        notes = [FakeNote(path="A.md", body="Embed ![[diagram.png]].\n")]
        graph = build_link_graph(notes, ["!attachments/diagram.png"])
        assert graph.unresolved == []
        assert graph.links_from("A.md") == []

    def test_links_to_unknown_path_is_empty(self):
        graph = build_link_graph([FakeNote(path="A.md")])
        assert graph.links_to("Nope.md") == []
