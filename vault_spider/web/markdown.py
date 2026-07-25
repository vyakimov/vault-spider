"""Render vault Markdown to HTML for the reading view.

Obsidian's dialect is CommonMark plus three things this vault leans on heavily:
wikilinks (94% of notes), callouts (57%), and `==highlight==`. Each gets a rule here.

Raw HTML is disabled at the parser, so anything in a note body that looks like a tag is
escaped rather than injected. Every string this module puts into HTML is escaped
explicitly; nothing reaches the page unquoted.

Math is deliberately **not** enabled. This vault has no block math, and every `$…$` in it
is a shell variable inside a code span — turning on a math rule would corrupt them.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.rules_inline import StateInline
from markdown_it.token import Token
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from vault_spider.corpus.links import WIKILINK_TOKEN_RE, Resolver, parse_wikilink

# `> [!NOTE]`, `> [!SUMMARY]-` (folded), `> [!TIP]+ With a title`
CALLOUT_RE = re.compile(r"^\s*\[!(?P<type>[\w-]+)\](?P<fold>[+-])?[ \t]*(?P<title>[^\n]*)")
MARK_RE = re.compile(r"==(?P<text>.+?)==", re.DOTALL)
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".bmp")

# Callout types actually used in this vault, mapped to the label shown to the reader.
# An unknown type still renders; it just falls back to its own name.
CALLOUT_LABELS = {
    "note": "Note",
    "summary": "Summary",
    "abstract": "Summary",
    "tldr": "Summary",
    "info": "Info",
    "important": "Important",
    "warning": "Warning",
    "caution": "Warning",
    "tip": "Tip",
    "hint": "Tip",
    "question": "Question",
    "example": "Example",
    "quote": "Quote",
    "success": "Success",
    "failure": "Failure",
    "danger": "Danger",
    "bug": "Bug",
    "todo": "To do",
}


@dataclass(frozen=True)
class Highlight:
    """A body line range to mark, 1-based and inclusive, as chunk metadata records it."""

    line_start: int
    line_end: int

    @property
    def anchor(self) -> str:
        return f"L{self.line_start}"


def heading_slug(text: str) -> str:
    """A stable anchor id for a heading, used by both `[[Note#Heading]]` and the toc."""
    slug = re.sub(r"[^\w\s-]", "", text.strip().lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "section"


def note_url(path: str, heading: str = "") -> str:
    url = "/note/" + quote(path)
    if heading:
        url += "#" + heading_slug(heading)
    return url


def attachment_url(path: str) -> str:
    return "/attachment/" + quote(path)


def _is_image(path: str) -> bool:
    return path.lower().endswith(IMAGE_SUFFIXES)


# ---------------------------------------------------------------------------
# Inline rules
# ---------------------------------------------------------------------------


def _wikilink_rule(state: StateInline, silent: bool) -> bool:
    """`[[Target#Heading|Alias]]` and `![[embed]]`.

    Registered before `link`, so a `[text](url)` link and an `![alt](url)` image both
    fall through untouched. Code spans never reach here: the `backticks` rule consumes
    them first, and fenced blocks are not inline-tokenized at all.
    """
    src = state.src
    pos = state.pos
    if src[pos] not in "![":
        return False
    match = WIKILINK_TOKEN_RE.match(src, pos)
    if match is None:
        return False
    if not silent:
        _emit_wikilink(state, parse_wikilink(match))
    state.pos = match.end()
    return True


def _emit_wikilink(state: StateInline, link) -> None:
    resolver: Optional[Resolver] = state.env.get("resolver")
    display = link.display

    # A same-note heading link: `[[#Section]]`.
    if not link.target:
        _push_link(state, "#" + heading_slug(link.heading), display, "wikilink")
        return

    resolved = resolver.resolve(link.target) if resolver else None
    if resolved is not None:
        _push_link(state, note_url(resolved, link.heading), display, "wikilink")
        return

    attachment = resolver.resolve_attachment(link.target) if resolver else None
    if attachment is not None:
        if link.is_embed and _is_image(attachment):
            alt = link.alias or link.target
            token = state.push("image", "img", 0)
            token.attrs = {"src": attachment_url(attachment), "alt": "", "loading": "lazy"}
            token.content = alt
            # markdown-it renders `alt` from the children, not the attr.
            alt_token = Token("text", "", 0)
            alt_token.content = alt
            token.children = [alt_token]
            return
        _push_link(state, attachment_url(attachment), display, "wikilink wikilink--file")
        return

    # Nothing of that name exists. Show the text, but never as a link — the interface
    # must not promise a destination it does not have.
    token = state.push("html_inline", "", 0)
    token.content = (
        f'<span class="wikilink wikilink--missing" '
        f'title="No note named &quot;{html.escape(link.target, quote=True)}&quot;">'
        f"{html.escape(display)}</span>"
    )


def _push_link(state: StateInline, href: str, text: str, css_class: str) -> None:
    open_token = state.push("link_open", "a", 1)
    open_token.attrs = {"href": href, "class": css_class}
    text_token = state.push("text", "", 0)
    text_token.content = text
    state.push("link_close", "a", -1)


def _mark_rule(state: StateInline, silent: bool) -> bool:
    """Obsidian's `==highlight==`, which no plugin ships."""
    src = state.src
    pos = state.pos
    if not src.startswith("==", pos):
        return False
    match = MARK_RE.match(src, pos)
    if match is None:
        return False
    if not silent:
        state.push("mark_open", "mark", 1)
        text_token = state.push("text", "", 0)
        text_token.content = match.group("text")
        state.push("mark_close", "mark", -1)
    state.pos = match.end()
    return True


# ---------------------------------------------------------------------------
# Core rules (run after `block`, before `inline`, so mutated content is re-parsed)
# ---------------------------------------------------------------------------


def _callout_rule(state: StateCore) -> None:
    """Turn `> [!TYPE] Title` blockquotes into callouts.

    Obsidian's fold markers are honoured: `-` and `+` make a callout collapsible,
    a bare `[!TYPE]` does not. The title line is lifted out of the body.
    """
    tokens = state.tokens
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.type != "blockquote_open":
            index += 1
            continue
        inline = _first_inline(tokens, index)
        if inline is None:
            index += 1
            continue
        match = CALLOUT_RE.match(inline.content)
        if match is None:
            index += 1
            continue

        kind = match.group("type").lower()
        fold = match.group("fold")
        title = match.group("title").strip()
        label = CALLOUT_LABELS.get(kind, match.group("type"))

        # Strip the marker line; whatever follows stays the callout's body.
        remainder = inline.content[match.end():].lstrip("\n")
        inline.content = remainder
        inline.children = None

        token.tag = "aside"
        classes = f"callout callout--{kind}"
        token.attrSet("class", classes)
        if fold:
            token.attrSet("data-fold", "open" if fold == "+" else "closed")
        _close_token(tokens, index).tag = "aside"

        header = Token("html_block", "", 0)
        header.content = _callout_header(label, title, kind)
        tokens.insert(index + 1, header)

        if not remainder.strip():
            _drop_empty_paragraph(tokens, index + 2)
        index += 2


def _callout_header(label: str, title: str, kind: str) -> str:
    shown = html.escape(title) if title else html.escape(label)
    return (
        f'<p class="callout__head"><span class="callout__label">{html.escape(label)}</span>'
        f'<span class="callout__title">{shown}</span></p>\n'
        if title
        else f'<p class="callout__head"><span class="callout__label">'
        f"{html.escape(label)}</span></p>\n"
    )


def _first_inline(tokens: List[Token], blockquote_index: int) -> Optional[Token]:
    if blockquote_index + 2 >= len(tokens):
        return None
    if tokens[blockquote_index + 1].type != "paragraph_open":
        return None
    candidate = tokens[blockquote_index + 2]
    return candidate if candidate.type == "inline" else None


def _close_token(tokens: List[Token], open_index: int) -> Token:
    depth = 0
    for index in range(open_index, len(tokens)):
        depth += tokens[index].nesting
        if depth == 0:
            return tokens[index]
    return tokens[-1]


def _drop_empty_paragraph(tokens: List[Token], paragraph_index: int) -> None:
    if (
        paragraph_index + 2 < len(tokens)
        and tokens[paragraph_index].type == "paragraph_open"
        and tokens[paragraph_index + 2].type == "paragraph_close"
    ):
        del tokens[paragraph_index: paragraph_index + 3]


def _highlight_rule(state: StateCore) -> None:
    """Mark the block tokens covering the retrieved section's line range.

    Works on `token.map` rather than slicing text, because the range routinely starts or
    ends inside a fenced block or a table, and slicing would produce broken markup.
    """
    highlight: Optional[Highlight] = state.env.get("highlight")
    if highlight is None:
        return
    # `map` is 0-based, end-exclusive; the metadata is 1-based, end-inclusive.
    start, end = highlight.line_start - 1, highlight.line_end
    first = True
    for token in state.tokens:
        # Opening tokens (nesting 1) and self-contained blocks such as `fence` and `hr`
        # (nesting 0) both carry attributes; closing tokens do not. `inline` tokens have
        # a map but render no attributes, so they are skipped.
        if token.map is None or token.nesting == -1 or token.type == "inline":
            continue
        token_start, token_end = token.map
        if token_start < end and start < token_end:
            token.attrJoin("class", "is-match")
            if first:
                token.attrSet("id", highlight.anchor)
                first = False


def _vault_image_rule(state: StateCore) -> None:
    """Point standard `![](relative/path.png)` images at the attachment route.

    Without this a vault image resolves against the web server and 404s.
    """
    for token in state.tokens:
        for child in token.children or []:
            if child.type != "image":
                continue
            src = child.attrGet("src")
            if not isinstance(src, str) or not src:
                continue
            if src.startswith(("http://", "https://", "data:", "/")):
                continue
            child.attrSet("src", attachment_url(src.lstrip("./")))
            child.attrSet("loading", "lazy")


def _drop_repeated_title_rule(state: StateCore) -> None:
    """Remove a leading H1 that just repeats the note's title.

    Most notes in this vault open with their own title as an H1. The reading view
    already sets that title above the body, and showing it twice costs a phone screen's
    worth of space before any content appears.
    """
    title: str = (state.env.get("drop_title") or "").strip().lower()
    if not title:
        return
    tokens = state.tokens
    if len(tokens) < 3 or tokens[0].type != "heading_open" or tokens[0].tag != "h1":
        return
    if tokens[1].type != "inline" or tokens[1].content.strip().lower() != title:
        return
    del tokens[0:3]


def _heading_anchor_rule(state: StateCore) -> None:
    """Give every heading a stable id so `[[Note#Heading]]` can land on it."""
    tokens = state.tokens
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        if index + 1 < len(tokens) and tokens[index + 1].type == "inline":
            token.attrSet("id", heading_slug(tokens[index + 1].content))


def _external_link_rule(state: StateCore) -> None:
    """External links open in a new tab; in-app links do not."""
    for token in state.tokens:
        for child in token.children or []:
            if child.type != "link_open":
                continue
            href = child.attrGet("href")
            if isinstance(href, str) and href.startswith(("http://", "https://")):
                child.attrJoin("class", "link--external")
                child.attrSet("target", "_blank")
                child.attrSet("rel", "noopener noreferrer")


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _parser() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    md.enable(["table", "strikethrough"])
    md.use(footnote_plugin)
    # Checkboxes stay disabled: this view is read-only, and a checkbox that visibly
    # accepts a click without saving anything is a lie.
    md.use(tasklists_plugin, enabled=False)

    md.inline.ruler.before("link", "wikilink", _wikilink_rule)
    md.inline.ruler.before("emphasis", "mark", _mark_rule)

    # Order matters: callouts rewrite inline content, so they must run before `inline`
    # tokenizes it. The rest only decorate tokens.
    md.core.ruler.after("block", "vs_drop_title", _drop_repeated_title_rule)
    md.core.ruler.after("vs_drop_title", "callout", _callout_rule)
    md.core.ruler.after("callout", "vs_highlight", _highlight_rule)
    md.core.ruler.after("vs_highlight", "vs_heading_anchor", _heading_anchor_rule)
    md.core.ruler.after("inline", "vs_vault_image", _vault_image_rule)
    md.core.ruler.after("vs_vault_image", "vs_external_link", _external_link_rule)
    return md


def render_markdown(
    body: str,
    *,
    resolver: Optional[Resolver] = None,
    highlight: Optional[Highlight] = None,
    drop_title: str = "",
) -> str:
    """Render a note body to HTML.

    ``resolver`` decides which wikilinks become links; without one, every wikilink
    renders as unresolved. ``highlight`` marks the retrieved section's line range.
    ``drop_title`` removes a leading H1 that repeats the note's own title.
    """
    env: Dict[str, Any] = {
        "resolver": resolver,
        "highlight": highlight,
        "drop_title": drop_title,
    }
    return _parser().render(body, env)


def render_inline(text: str) -> str:
    """Render a short fragment (a synthesized answer, an excerpt) with no vault context."""
    return _parser().render(text, {"resolver": None, "highlight": None})


def outline(body: str) -> List[Tuple[int, str, str]]:
    """Headings as (level, text, anchor), for a table of contents."""
    result: List[Tuple[int, str, str]] = []
    tokens = _parser().parse(body, {"resolver": None, "highlight": None})
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        if index + 1 < len(tokens) and tokens[index + 1].type == "inline":
            text = tokens[index + 1].content.strip()
            result.append((int(token.tag[1:]), text, heading_slug(text)))
    return result
