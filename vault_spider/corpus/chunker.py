"""Deterministic, Markdown-aware section splitting for notes (no LLM)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Tuple

from markdown_it import MarkdownIt

from vault_spider.corpus.loader import Note

CHUNK_SCHEMA_VERSION = 2
TARGET_TOKENS = 450
MIN_TOKENS = 300
MAX_TOKENS = 600
HARD_MAX_TOKENS = 900
PROSE_OVERLAP_TOKENS = 50

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
_CJK_RE = re.compile(
    "[\u2e80-\u2eff\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf"
    "\u4e00-\u9fff\uf900-\ufaff]"
)
_SENTENCE_RE = re.compile(r".+?(?:[.!?](?=\s|$)|$)\s*", re.DOTALL)


@dataclass
class Section:
    chunk_id: str        # f"{note_id}::s{index:03d}"
    note_id: str
    heading: str         # nearest H1-H3 heading ("" for preamble)
    level: int           # H1-H3 level, 0 for preamble
    line_start: int      # 1-based, inclusive, within the BODY
    line_end: int        # 1-based, inclusive
    text: str
    heading_path: Tuple[str, ...] = ()
    parent_section_id: str = ""
    token_count: int = 0


@dataclass(frozen=True)
class _Block:
    start0: int
    end0: int  # 0-based, exclusive
    text: str
    kind: str
    heading: str
    level: int
    heading_path: Tuple[str, ...]
    parent_section_id: str
    fragmented: bool = False

    @property
    def token_count(self) -> int:
        return estimate_tokens(self.text)


def estimate_tokens(text: str) -> int:
    """Return a deterministic, model-independent token estimate.

    Word runs count once, punctuation counts individually, and CJK word runs
    count per character. The estimator is intentionally conservative enough
    for chunk budgeting without coupling the corpus layer to one model.
    """
    count = 0
    for match in _TOKEN_RE.finditer(text):
        value = match.group(0)
        cjk = _CJK_RE.findall(value)
        count += len(cjk) if cjk else 1
    return count


@lru_cache(maxsize=1)
def _parser() -> MarkdownIt:
    return MarkdownIt(
        "commonmark",
        {"html": False, "linkify": False, "typographer": False},
    ).enable(["table", "strikethrough"])


def _heading_text(tokens, index: int) -> str:
    if index + 1 < len(tokens) and tokens[index + 1].type == "inline":
        return tokens[index + 1].content.strip()
    return ""


def _markdown_blocks(note: Note) -> List[_Block]:
    lines = note.body.split("\n")
    tokens = _parser().parse(note.body)
    heading_stack: dict[int, str] = {}
    parent_heading = ""
    parent_level = 0
    parent_index = 0
    blocks: List[_Block] = []

    for index, token in enumerate(tokens):
        if token.level != 0 or token.map is None or token.nesting == -1:
            continue
        if token.type.endswith("_close") or token.type == "inline":
            continue

        start0, end0 = token.map
        if end0 <= start0:
            continue

        if token.type == "heading_open":
            level = int(token.tag[1:])
            text = _heading_text(tokens, index)
            for stale_level in [value for value in heading_stack if value >= level]:
                del heading_stack[stale_level]
            heading_stack[level] = text
            if level <= 3:
                parent_index += 1
                parent_heading = text
                parent_level = level

        heading_path = tuple(
            heading_stack[level] for level in sorted(heading_stack) if heading_stack[level]
        )
        kind = token.type.removesuffix("_open")
        blocks.append(
            _Block(
                start0=start0,
                end0=end0,
                text="\n".join(lines[start0:end0]),
                kind=kind,
                heading=parent_heading,
                level=parent_level,
                heading_path=heading_path,
                parent_section_id=f"{note.note_id}::p{parent_index:03d}",
            )
        )
    if blocks and blocks[-1].end0 < len(lines):
        last = blocks[-1]
        blocks[-1] = _Block(
            start0=last.start0,
            end0=len(lines),
            text="\n".join(lines[last.start0:]),
            kind=last.kind,
            heading=last.heading,
            level=last.level,
            heading_path=last.heading_path,
            parent_section_id=last.parent_section_id,
        )
    return blocks


def _largest_prefix_within(text: str, budget: int) -> int:
    low, high = 1, len(text)
    best = 1
    while low <= high:
        middle = (low + high) // 2
        if estimate_tokens(text[:middle]) <= budget:
            best = middle
            low = middle + 1
        else:
            high = middle - 1
    whitespace = max(text.rfind(" ", 0, best), text.rfind("\t", 0, best))
    if whitespace >= max(1, best // 2):
        return whitespace + 1
    return best


def _hard_text_fragments(text: str, budget: int) -> List[Tuple[int, int, str]]:
    fragments: List[Tuple[int, int, str]] = []
    cursor = 0
    while cursor < len(text):
        remainder = text[cursor:]
        if estimate_tokens(remainder) <= budget:
            fragments.append((cursor, len(text), remainder))
            break
        width = _largest_prefix_within(remainder, budget)
        fragments.append((cursor, cursor + width, remainder[:width]))
        cursor += width
    return fragments


def _sentence_fragments(text: str, budget: int) -> List[Tuple[int, int, str]]:
    matches = [match for match in _SENTENCE_RE.finditer(text) if match.group(0)]
    if len(matches) <= 1:
        return _hard_text_fragments(text, budget)

    units: List[Tuple[int, int, str]] = []
    for match in matches:
        sentence = match.group(0)
        if estimate_tokens(sentence) <= budget:
            units.append((match.start(), match.end(), sentence))
            continue
        units.extend(
            (match.start() + start, match.start() + end, fragment)
            for start, end, fragment in _hard_text_fragments(sentence, budget)
        )

    groups: List[List[Tuple[int, int, str]]] = []
    current: List[Tuple[int, int, str]] = []
    current_text = ""
    for unit in units:
        sentence = unit[2]
        candidate = current_text + sentence
        if current and estimate_tokens(candidate) > budget:
            groups.append(current)
            overlap: List[Tuple[int, int, str]] = []
            overlap_text = ""
            for prior in reversed(current):
                next_text = prior[2] + overlap_text
                if estimate_tokens(next_text) > PROSE_OVERLAP_TOKENS:
                    break
                overlap.insert(0, prior)
                overlap_text = next_text
            current = overlap
            current_text = overlap_text
        current.append(unit)
        current_text += sentence
    if current:
        groups.append(current)

    return [
        (group[0][0], group[-1][1], text[group[0][0] : group[-1][1]])
        for group in groups
    ]


def _fragment_line_range(block: _Block, start: int, end: int) -> Tuple[int, int]:
    before = block.text[:start]
    through = block.text[:end]
    start0 = block.start0 + before.count("\n")
    end0 = block.start0 + through.count("\n")
    if not through.endswith("\n"):
        end0 += 1
    return start0, max(start0 + 1, min(block.end0, end0))


def _line_offsets(text: str) -> List[int]:
    offsets = [0]
    for match in re.finditer("\n", text):
        offsets.append(match.end())
    offsets.append(len(text))
    return offsets


def _pack_line_spans(
    block: _Block,
    spans: List[Tuple[int, int]],
) -> List[Tuple[int, int, str]]:
    """Pack source-line spans without cutting an atomic row/item when possible."""
    offsets = _line_offsets(block.text)
    fragments: List[Tuple[int, int, str]] = []
    current_start: Optional[int] = None
    current_end: Optional[int] = None

    def flush() -> None:
        nonlocal current_start, current_end
        if current_start is None or current_end is None:
            return
        fragments.append(
            (
                offsets[current_start],
                offsets[current_end],
                block.text[offsets[current_start] : offsets[current_end]],
            )
        )
        current_start = None
        current_end = None

    for start_line, end_line in spans:
        start = offsets[start_line]
        end = offsets[end_line]
        unit = block.text[start:end]
        if estimate_tokens(unit) > HARD_MAX_TOKENS:
            flush()
            fragments.extend(
                (start + local_start, start + local_end, text)
                for local_start, local_end, text in _hard_text_fragments(
                    unit, HARD_MAX_TOKENS
                )
            )
            continue
        if current_start is None:
            current_start, current_end = start_line, end_line
            continue
        candidate = block.text[offsets[current_start] : end]
        if estimate_tokens(candidate) > HARD_MAX_TOKENS:
            flush()
            current_start, current_end = start_line, end_line
        else:
            current_end = end_line
    flush()
    return fragments


def _structural_line_spans(block: _Block) -> List[Tuple[int, int]]:
    """Return preferred split units for an oversized Markdown container."""
    line_count = len(block.text.splitlines())
    if block.text.endswith("\n"):
        line_count += 1
    if line_count <= 1:
        return [(0, 1)]

    if block.kind in {"bullet_list", "ordered_list"}:
        item_spans = [
            tuple(token.map)
            for token in _parser().parse(block.text)
            if token.type == "list_item_open"
            and token.level == 1
            and token.map is not None
        ]
        if item_spans:
            return [(int(start), int(end)) for start, end in item_spans]

    if block.kind == "table":
        row_spans = [
            tuple(token.map)
            for token in _parser().parse(block.text)
            if token.type == "tr_open" and token.map is not None
        ]
        if row_spans:
            spans: List[Tuple[int, int]] = []
            first_start, first_end = row_spans[0]
            # Markdown-it's header-row map omits the delimiter row. Keep both
            # together so the first fragment remains valid table source.
            spans.append((int(first_start), min(line_count, int(first_end) + 1)))
            spans.extend(
                (int(start), int(end)) for start, end in row_spans[1:]
            )
            return spans

    # Fences, blockquotes/callouts, and other oversized atomic blocks split at
    # source line boundaries before the final same-line character fallback.
    return [(line, line + 1) for line in range(line_count)]


def _split_oversize_block(block: _Block) -> List[_Block]:
    if block.token_count <= HARD_MAX_TOKENS:
        return [block]
    if block.kind == "paragraph":
        fragments = _sentence_fragments(block.text, HARD_MAX_TOKENS)
    else:
        fragments = _pack_line_spans(block, _structural_line_spans(block))

    split: List[_Block] = []
    for start, end, text in fragments:
        start0, end0 = _fragment_line_range(block, start, end)
        split.append(
            _Block(
                start0=start0,
                end0=end0,
                text=text,
                kind=block.kind,
                heading=block.heading,
                level=block.level,
                heading_path=block.heading_path,
                parent_section_id=block.parent_section_id,
                fragmented=True,
            )
        )
    return split


def _same_context(left: _Block, right: _Block) -> bool:
    return (
        left.parent_section_id == right.parent_section_id
        and left.heading_path == right.heading_path
    )


def _group_blocks(blocks: List[_Block]) -> List[List[_Block]]:
    groups: List[List[_Block]] = []
    current: List[_Block] = []
    current_tokens = 0
    for block in blocks:
        if (
            current
            and (
                not _same_context(current[-1], block)
                or current_tokens + block.token_count > MAX_TOKENS
            )
        ):
            groups.append(current)
            current = []
            current_tokens = 0
        current.append(block)
        current_tokens += block.token_count
    if current:
        groups.append(current)

    merged: List[List[_Block]] = []
    for group in groups:
        group_tokens = sum(block.token_count for block in group)
        if (
            merged
            and group_tokens < MIN_TOKENS
            and _same_context(merged[-1][-1], group[0])
            and sum(block.token_count for block in merged[-1]) + group_tokens
            <= HARD_MAX_TOKENS
        ):
            merged[-1].extend(group)
        else:
            merged.append(group)
    return merged


def _group_text(group: List[_Block], body_lines: List[str]) -> str:
    if (
        not any(block.fragmented for block in group)
        or (
            len(group) > 1
            and all(
                left.end0 <= right.start0
                for left, right in zip(group, group[1:])
            )
        )
    ):
        return "\n".join(body_lines[group[0].start0 : group[-1].end0])
    return "\n".join(block.text.rstrip("\n") for block in group).strip()


def _legacy_segment_lines(lines: List[str]) -> List[Tuple[str, int, int, int]]:
    """Old H1-H3 splitter retained for explicit max_chars test/tool callers."""
    in_fence = False
    starts: List[Tuple[int, str, int]] = []
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match and 1 <= len(match.group(1)) <= 3:
            starts.append((index, match.group(2).strip(), len(match.group(1))))

    n = len(lines)
    if not starts:
        return [("", 0, 0, n - 1)]
    segments: List[Tuple[str, int, int, int]] = []
    if starts[0][0] > 0:
        segments.append(("", 0, 0, starts[0][0] - 1))
    for position, (index, heading, level) in enumerate(starts):
        end = starts[position + 1][0] - 1 if position + 1 < len(starts) else n - 1
        segments.append((heading, level, index, end))
    return segments


def _legacy_windows(
    seg_lines: List[str], max_chars: int, overlap_chars: int
) -> List[Tuple[int, int]]:
    windows: List[Tuple[int, int]] = []
    start = 0
    while start < len(seg_lines):
        current = 0
        end = start
        for index in range(start, len(seg_lines)):
            added = len(seg_lines[index]) + (1 if index > start else 0)
            if index > start and current + added > max_chars:
                break
            current += added
            end = index
        windows.append((start, end))
        if end >= len(seg_lines) - 1:
            break
        overlap = 0
        next_start = end + 1
        for index in range(end, start, -1):
            added = len(seg_lines[index]) + 1
            if overlap + added > overlap_chars:
                break
            overlap += added
            next_start = index
        start = max(start + 1, next_start)
    return windows


def _legacy_split(
    note: Note, max_chars: int, overlap_chars: int
) -> List[Section]:
    lines = note.body.split("\n")
    sections: List[Section] = []
    for parent_index, (heading, level, start0, end0) in enumerate(
        _legacy_segment_lines(lines)
    ):
        segment = lines[start0 : end0 + 1]
        if level == 0 and not "\n".join(segment).strip():
            continue
        for win_start, win_end in _legacy_windows(segment, max_chars, overlap_chars):
            body_start0 = start0 + win_start
            body_end0 = start0 + win_end
            index = len(sections)
            text = "\n".join(lines[body_start0 : body_end0 + 1])
            sections.append(
                Section(
                    chunk_id=f"{note.note_id}::s{index:03d}",
                    note_id=note.note_id,
                    heading=heading,
                    level=level,
                    line_start=body_start0 + 1,
                    line_end=body_end0 + 1,
                    text=text,
                    heading_path=(heading,) if heading else (),
                    parent_section_id=f"{note.note_id}::p{parent_index:03d}",
                    token_count=estimate_tokens(text),
                )
            )
    return sections


def split_sections(
    note: Note,
    max_chars: Optional[int] = None,
    overlap_chars: int = 300,
) -> List[Section]:
    """Split one note into deterministic, structure-aware retrieval chunks.

    ``max_chars`` remains as a compatibility seam for callers explicitly
    exercising the former character-window behavior. Production calls omit it.
    """
    if max_chars is not None:
        return _legacy_split(note, max_chars, overlap_chars)
    if not note.body.strip():
        return []

    raw_blocks = _markdown_blocks(note)
    blocks = [
        fragment
        for block in raw_blocks
        for fragment in _split_oversize_block(block)
    ]
    body_lines = note.body.split("\n")
    sections: List[Section] = []
    for group in _group_blocks(blocks):
        text = _group_text(group, body_lines)
        if not text.strip():
            continue
        first, last = group[0], group[-1]
        index = len(sections)
        sections.append(
            Section(
                chunk_id=f"{note.note_id}::s{index:03d}",
                note_id=note.note_id,
                heading=first.heading,
                level=first.level,
                line_start=first.start0 + 1,
                line_end=last.end0,
                text=text,
                heading_path=first.heading_path,
                parent_section_id=first.parent_section_id,
                token_count=estimate_tokens(text),
            )
        )
    return sections


def document_text(
    note: Note,
    context: str = "",
    context_label: str = "Context",
) -> str:
    parts = [f"# {note.title}", f"Path: {note.path}"]
    if note.tags:
        parts.append(f"Tags: {', '.join(note.tags)}")
    if note.date:
        parts.append(f"Date: {note.date}")
    if context:
        parts.append(f"{context_label}: {context}")
    if note.body.strip():
        parts.append(note.body.strip())
    return "\n\n".join(parts).strip()


def document_source_offset(
    note: Note,
    context: str = "",
    context_label: str = "Context",
) -> int:
    text = document_text(note, context, context_label)
    source = note.body.strip()
    return len(text) - len(source) if source else len(text)


def section_prefix(
    note: Note,
    section: Section,
    context: str = "",
    context_label: str = "Context",
) -> str:
    """Section header, optionally carrying one canonical note summary.

    Kept deliberately small. A wider provenance block (type, tags, full heading
    path) was measured and did not pay for itself, and every line here competes
    with the chunk body for the embedding's attention.
    """
    prefix = f"# {note.title}\n\nSection: {section.heading or '(intro)'}\n\n"
    if context:
        prefix += f"{context_label}: {context}\n\n"
    return prefix


def section_text(
    note: Note,
    section: Section,
    context: str = "",
    context_label: str = "Context",
) -> str:
    return section_prefix(note, section, context, context_label) + section.text


def section_source_offset(
    note: Note,
    section: Section,
    context: str = "",
    context_label: str = "Context",
) -> int:
    return len(section_prefix(note, section, context, context_label))
