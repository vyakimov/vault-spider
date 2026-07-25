"""Wikilink extraction, Obsidian-compatible resolution, and the vault link graph.

This is the single implementation of "what does `[[Target]]` point at" and "what links
here". Both the lint report and the reading view depend on resolving links exactly the
way Obsidian does, so the rules live here rather than in either caller.

Callers supply their own note objects; anything with the attributes named by
:class:`ResolvableNote` / :class:`LinkNode` works, which keeps this module free of a
dependency on ``compounding.lint`` or the web layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol, Sequence, Set, Tuple

# Matches a wikilink and captures only the target, dropping any `#heading` and `|alias`.
# Kept as the historical name because the lint findings and the note-mutation contract
# both match against it.
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

# The rendering form: every part addressable, and `![[...]]` embeds distinguished from
# plain links. An empty target means a same-note link such as `[[#Section]]`.
WIKILINK_TOKEN_RE = re.compile(
    r"(?P<embed>!)?\[\["
    r"(?P<target>[^\]|#]*)"
    r"(?:#(?P<heading>[^\]|]*))?"
    r"(?:\|(?P<alias>[^\]]*))?"
    r"\]\]"
)


class ResolvableNote(Protocol):
    """A note as the resolver sees it: the names it can be reached by."""

    path: str  # vault-relative posix
    stem: str
    title: str
    aliases: List[str]


class LinkNode(ResolvableNote, Protocol):
    """A note as the graph builder sees it: also the text its links live in."""

    body: str
    frontmatter_text: str


@dataclass(frozen=True)
class Wikilink:
    """One parsed wikilink occurrence."""

    target: str  # "" for a same-note heading link
    heading: str
    alias: str
    is_embed: bool
    raw: str

    @property
    def display(self) -> str:
        """What the reader should see, following Obsidian's precedence."""
        if self.alias:
            return self.alias
        if self.target and self.heading:
            return f"{self.target} › {self.heading}"
        return self.target or self.heading


@dataclass(frozen=True)
class UnresolvedLink:
    """A wikilink that names neither a note nor an attachment."""

    path: str  # the note containing the link
    target: str
    line: int
    location: str  # "body" (body-relative line) or "frontmatter" (file-relative)


def parse_wikilink(match: "re.Match[str]") -> Wikilink:
    """Build a :class:`Wikilink` from a :data:`WIKILINK_TOKEN_RE` match."""
    return Wikilink(
        target=(match.group("target") or "").strip(),
        heading=(match.group("heading") or "").strip(),
        alias=(match.group("alias") or "").strip(),
        is_embed=match.group("embed") is not None,
        raw=match.group(0),
    )


def extract_frontmatter_wikilinks(frontmatter_text: str) -> List[Tuple[str, int]]:
    """Return (target, file line) for wikilinks in frontmatter values.

    Obsidian treats `parents: "[[Daily Notes]]"` as a real link; so do we. Lines are
    file-relative (frontmatter starts at line 1), unlike body links, whose lines are
    body-relative — each finding records which via its ``location`` field.
    """
    results: List[Tuple[str, int]] = []
    for index, line in enumerate(frontmatter_text.split("\n"), start=2):  # line 1 is `---`
        for match in WIKILINK_RE.finditer(line):
            results.append((match.group(1).strip(), index))
    return results


def extract_wikilinks(body: str) -> List[Tuple[str, int]]:
    """Return (target, 1-based line) for wikilinks outside fences and backticks."""
    results: List[Tuple[str, int]] = []
    in_fence = False
    for index, line in enumerate(body.split("\n"), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        cleaned = INLINE_CODE_RE.sub("", line)
        for match in WIKILINK_RE.finditer(cleaned):
            results.append((match.group(1).strip(), index))
    return results


class Resolver:
    """Resolves a wikilink target the way Obsidian does.

    Beyond note titles/stems/paths this covers two cases the vault relies on:
    frontmatter ``aliases``, and attachments — `[[diagram.png]]` names a real file
    even though it is not a note, so it must not be reported as a broken link.
    """

    def __init__(self, notes: Sequence[ResolvableNote], attachments: Iterable[str] = ()):
        self.by_title: Dict[str, str] = {}
        self.by_stem: Dict[str, str] = {}
        self.by_path: Dict[str, str] = {}
        self.by_alias: Dict[str, str] = {}
        self.attachments: Dict[str, str] = {}
        for note in notes:
            self.by_title.setdefault(note.title.lower(), note.path)
            self.by_stem.setdefault(note.stem.lower(), note.path)
            self.by_path.setdefault(note.path.lower(), note.path)
            if note.path.lower().endswith(".md"):
                self.by_path.setdefault(note.path[:-3].lower(), note.path)
            for alias in note.aliases:
                self.by_alias.setdefault(alias.lower(), note.path)
        for rel in attachments:
            self.attachments.setdefault(rel.lower(), rel)
            name = Path(rel).name
            self.attachments.setdefault(name.lower(), rel)
            if name.lower().endswith(".md"):
                # `[[map0.excalidraw]]` names `Excalidraw/map0.excalidraw.md`.
                self.attachments.setdefault(name[:-3].lower(), rel)

    def resolve(self, target: str) -> Optional[str]:
        """Resolve to a note path, or None. Attachments resolve via `resolve_attachment`."""
        key = target.strip().lower()
        for table in (self.by_title, self.by_stem, self.by_path, self.by_alias):
            if key in table:
                return table[key]
        if not key.endswith(".md") and (key + ".md") in self.by_path:
            return self.by_path[key + ".md"]
        return None

    def resolve_attachment(self, target: str) -> Optional[str]:
        return self.attachments.get(target.strip().lower())


@dataclass
class LinkGraph:
    """Resolved wikilink edges over a whole vault, plus what did not resolve."""

    resolver: Resolver
    outgoing: Dict[str, Set[str]] = field(default_factory=dict)
    incoming: Dict[str, Set[str]] = field(default_factory=dict)
    unresolved: List[UnresolvedLink] = field(default_factory=list)

    def links_from(self, path: str) -> List[str]:
        """Notes this note links to, sorted."""
        return sorted(self.outgoing.get(path, set()))

    def links_to(self, path: str) -> List[str]:
        """Backlinks: notes that link to this note, sorted."""
        return sorted(self.incoming.get(path, set()))


def build_link_graph(
    notes: Sequence[LinkNode],
    attachments: Iterable[str] = (),
) -> LinkGraph:
    """Resolve every wikilink in ``notes`` into a graph.

    Frontmatter links (`parents: "[[Daily Notes]]"`) count exactly like body links.
    Attachments resolve to files rather than notes, so they are neither edges nor
    unresolved. Self-links are dropped from the graph but are not reported.
    """
    graph = LinkGraph(
        resolver=Resolver(notes, attachments),
        outgoing={note.path: set() for note in notes},
        incoming={note.path: set() for note in notes},
    )
    for note in notes:
        occurrences = [
            (target, line, "body") for target, line in extract_wikilinks(note.body)
        ] + [
            (target, line, "frontmatter")
            for target, line in extract_frontmatter_wikilinks(note.frontmatter_text)
        ]
        for target, line, location in occurrences:
            resolved = graph.resolver.resolve(target)
            if resolved is None:
                if graph.resolver.resolve_attachment(target) is not None:
                    continue  # a real file, just not a note
                graph.unresolved.append(
                    UnresolvedLink(path=note.path, target=target, line=line, location=location)
                )
            elif resolved != note.path:
                graph.outgoing[note.path].add(resolved)
                graph.incoming[resolved].add(note.path)
    return graph
