"""Tests for vault_spider.web.markdown — the reading view's renderer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pytest

from vault_spider.corpus.links import Resolver
from vault_spider.web.markdown import Highlight, heading_slug, outline, render_markdown


@dataclass
class Note:
    path: str
    title: str = ""
    aliases: List[str] = field(default_factory=list)

    @property
    def stem(self) -> str:
        return self.path.rsplit("/", 1)[-1].removesuffix(".md")

    def __post_init__(self):
        if not self.title:
            self.title = self.stem


@pytest.fixture
def resolver() -> Resolver:
    return Resolver(
        [Note(path="Infra/VPN.md", title="WireGuard setup", aliases=["The VPN"])],
        ["!attachments/diagram.png", "docs/manual.pdf"],
    )


def render(body: str, resolver: Resolver | None = None, **kwargs) -> str:
    return render_markdown(body, resolver=resolver, **kwargs)


class TestWikilinks:
    def test_resolved_link_becomes_an_anchor(self, resolver):
        html = render("See [[VPN]].", resolver)
        assert '<a href="/note/Infra/VPN.md" class="wikilink">VPN</a>' in html

    def test_resolves_by_title_and_alias(self, resolver):
        assert '/note/Infra/VPN.md' in render("[[WireGuard setup]]", resolver)
        assert '/note/Infra/VPN.md' in render("[[The VPN]]", resolver)

    def test_alias_is_the_display_text(self, resolver):
        assert ">the guide</a>" in render("[[VPN|the guide]]", resolver)

    def test_heading_becomes_a_fragment(self, resolver):
        assert 'href="/note/Infra/VPN.md#key-rotation"' in render(
            "[[VPN#Key rotation]]", resolver
        )

    def test_unresolved_link_is_not_an_anchor(self, resolver):
        html = render("See [[Nowhere]].", resolver)
        assert "<a" not in html
        assert 'class="wikilink wikilink--missing"' in html
        assert ">Nowhere</span>" in html

    def test_same_note_heading_link(self, resolver):
        assert 'href="#a-section"' in render("[[#A section]]", resolver)

    def test_image_embed_becomes_an_img(self, resolver):
        html = render("![[diagram.png]]", resolver)
        assert 'src="/attachment/%21attachments/diagram.png"' in html
        assert 'loading="lazy"' in html

    def test_embed_alt_text_comes_from_the_alias(self, resolver):
        assert 'alt="A diagram"' in render("![[diagram.png|A diagram]]", resolver)

    def test_non_image_attachment_becomes_a_link(self, resolver):
        html = render("[[manual.pdf]]", resolver)
        assert 'href="/attachment/docs/manual.pdf"' in html

    def test_without_a_resolver_every_wikilink_is_missing(self):
        assert "wikilink--missing" in render("[[VPN]]")

    def test_wikilink_in_a_code_span_is_left_alone(self, resolver):
        html = render("Use `[[NotALink]]` here.", resolver)
        assert "<code>[[NotALink]]</code>" in html
        assert "wikilink" not in html

    def test_wikilink_in_a_fence_is_left_alone(self, resolver):
        html = render("```\n[[NotALink]]\n```\n", resolver)
        assert "wikilink" not in html

    def test_ordinary_markdown_links_still_work(self, resolver):
        html = render("[text](https://example.com)", resolver)
        assert 'href="https://example.com"' in html
        assert 'rel="noopener noreferrer"' in html

    def test_path_is_percent_encoded(self):
        html = render("[[My Note]]", Resolver([Note(path="200 Tech/My Note.md")]))
        assert "/note/200%20Tech/My%20Note.md" in html


class TestCallouts:
    @pytest.mark.parametrize(
        "kind,label",
        [("NOTE", "Note"), ("SUMMARY", "Summary"), ("IMPORTANT", "Important"),
         ("INFO", "Info"), ("WARNING", "Warning"), ("note", "Note"), ("Example", "Example")],
    )
    def test_types_used_in_this_vault(self, kind, label):
        html = render(f"> [!{kind}]\n> Body.\n")
        assert f'class="callout callout--{kind.lower()}"' in html
        assert f">{label}</span>" in html
        assert "<p>Body.</p>" in html

    def test_title_is_lifted_out_of_the_body(self):
        html = render("> [!NOTE] Remember this\n> The body.\n")
        assert '<span class="callout__title">Remember this</span>' in html
        assert "<p>The body.</p>" in html
        assert "Remember this</p>" not in html.split("callout__head")[1].split("</p>")[1]

    def test_body_markdown_is_rendered(self, resolver):
        html = render("> [!NOTE] T\n> With [[VPN]] and **bold**.\n", resolver)
        assert 'class="wikilink"' in html
        assert "<strong>bold</strong>" in html

    def test_fold_marker_is_honoured(self):
        assert 'data-fold="closed"' in render("> [!TIP]- Folded\n> Hidden.\n")
        assert 'data-fold="open"' in render("> [!TIP]+ Open\n> Shown.\n")
        assert "data-fold" not in render("> [!TIP] Plain\n> Shown.\n")

    def test_unknown_type_still_renders(self):
        html = render("> [!Prompt] Ask\n> Body.\n")
        assert 'class="callout callout--prompt"' in html
        assert ">Prompt</span>" in html

    def test_plain_blockquote_is_untouched(self):
        html = render("> Just a quotation.\n")
        assert "<blockquote>" in html
        assert "callout" not in html


class TestSafety:
    def test_raw_html_is_escaped(self):
        html = render("<script>alert(1)</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_html_in_a_wikilink_target_is_escaped(self):
        html = render('[[<img src=x onerror=alert(1)>]]')
        assert "<img" not in html
        assert "onerror" not in html or "&lt;" in html

    def test_shell_variables_in_code_survive_untouched(self):
        """This vault's only `$…$` are shell variables; math must stay off."""
        body = "```bash\ncd $HOME/.cfg && echo $(id -u) $(id -g)\n```\n"
        html = render(body)
        assert "$HOME/.cfg" in html
        assert "$(id -u)" in html
        assert "math" not in html

    def test_inline_shell_variables_survive(self):
        assert "$HOME" in render("Set `$HOME` and `$USER` first.")


class TestVaultFeatures:
    def test_highlight_marks_only_the_matched_lines(self):
        body = "line one\n\nline two\n\nline three\n"
        html = render(body, highlight=Highlight(3, 3))
        assert '<p class="is-match" id="L3">line two</p>' in html
        assert "<p>line one</p>" in html
        assert "<p>line three</p>" in html

    def test_highlight_spanning_a_fence_does_not_break_markup(self):
        body = "intro\n\n```python\nx = 1\ny = 2\n```\n\nafter\n"
        html = render(body, highlight=Highlight(3, 6))
        # The whole fence is marked as one block; the code is not sliced apart.
        assert html.count("<pre") == 1
        assert "is-match" in html
        assert "x = 1\ny = 2" in html

    def test_no_highlight_marks_nothing(self):
        assert "is-match" not in render("line one\n")

    def test_mark_syntax(self):
        assert "<mark>important</mark>" in render("Some ==important== text.")

    def test_tables_render(self):
        html = render("| a | b |\n|---|---|\n| 1 | 2 |\n")
        assert "<table>" in html and "<td>1</td>" in html

    def test_task_lists_render_disabled(self):
        html = render("- [ ] todo\n- [x] done\n")
        assert 'type="checkbox"' in html
        assert "disabled" in html

    def test_footnotes_render(self):
        html = render("Claim.[^1]\n\n[^1]: The source.\n")
        assert "footnote" in html

    def test_headings_get_anchors(self):
        assert '<h2 id="my-heading">' in render("## My heading\n")

    def test_relative_images_point_at_the_attachment_route(self):
        assert 'src="/attachment/assets/pic.png"' in render("![alt](assets/pic.png)")

    def test_absolute_images_are_left_alone(self):
        assert 'src="https://example.com/p.png"' in render("![](https://example.com/p.png)")

    def test_repeated_title_heading_is_dropped(self):
        html = render("# My Note\n\nBody.\n", drop_title="My Note")
        assert "<h1" not in html
        assert "<p>Body.</p>" in html

    def test_a_different_first_heading_is_kept(self):
        html = render("# Something else\n\nBody.\n", drop_title="My Note")
        assert "<h1" in html

    def test_title_dropping_is_opt_in(self):
        assert "<h1" in render("# My Note\n\nBody.\n")


class TestHelpers:
    @pytest.mark.parametrize(
        "text,slug",
        [("My Heading", "my-heading"), ("Key rotation!", "key-rotation"),
         ("  Spaced  out  ", "spaced-out"), ("###", "section"), ("", "section")],
    )
    def test_heading_slug(self, text, slug):
        assert heading_slug(text) == slug

    def test_outline_lists_headings(self):
        result = outline("# One\n\ntext\n\n## Two\n")
        assert result == [(1, "One", "one"), (2, "Two", "two")]
