"""Turning retrieval contracts into things a reader can look at.

The retrieval contract is built for machines: excerpts carry the synthesized indexing
header, and scores are raw values on four different scales. Both need work before a
person should see them. None of this changes the contract itself — the JSON route serves
`build_retrieval_output` untouched.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import quote, urlencode

# `document_text()` prefixes every indexed document with a synthesized header, and every
# section entry with `Section: <heading>`. Neither is in the note; both must go before
# the excerpt is shown, or every result opens with "Path: ...".
SYNTHETIC_PREFIX_RE = re.compile(
    r"\A(?:#\s+[^\n]*\n+)?"
    r"(?:(?:Path|Tags|Date|Section):[^\n]*\n+)*"
)


def clean_excerpt(text: str) -> str:
    """The excerpt without the indexer's synthesized header."""
    return SYNTHETIC_PREFIX_RE.sub("", text or "", count=1).strip()


# Markdown syntax that should not appear in a preview. The excerpt is a 700-char cut of
# the indexed text, so it routinely ends mid-construct — rendering it as Markdown would
# produce broken markup. Stripping to prose is both safer and easier to skim.
_PREVIEW_RULES = (
    (re.compile(r"^#{1,6}\s+", re.MULTILINE), ""),  # heading markers
    # Wikilinks show their alias when they have one, their target otherwise.
    (
        re.compile(r"!?\[\[([^\]|#]*)(?:#([^\]|]*))?(?:\|([^\]]*))?\]\]"),
        lambda m: m.group(3) or m.group(1) or m.group(2) or "",
    ),
    (re.compile(r"!?\[([^\]]*)\]\([^)]*\)"), r"\1"),  # inline links and images
    (re.compile(r"`{1,3}"), ""),  # code ticks
    (re.compile(r"^\s*>\s?\[![\w-]+\][+-]?\s*", re.MULTILINE), ""),  # callout markers
    (re.compile(r"^\s*>\s?", re.MULTILINE), ""),  # blockquote markers
    (re.compile(r"^\s*[-*+]\s+(?:\[[ xX]\]\s+)?", re.MULTILINE), ""),  # list bullets
    (re.compile(r"(\*\*|__|==|~~)"), ""),  # emphasis and highlight
    (re.compile(r"\s*\n\s*"), " "),  # collapse to one flowing line
)


def preview(text: str, title: str = "") -> str:
    """A result excerpt as plain prose, with the Markdown taken out.

    Readers are judging relevance here, not reading the note — literal `[[wikilinks]]`
    and `##` in a preview are noise standing between them and that judgement.

    Notes in this vault commonly repeat their title as the body's first heading. That
    line is already shown above the excerpt, so it is dropped rather than shown twice.
    """
    result = clean_excerpt(text)
    for pattern, replacement in _PREVIEW_RULES:
        result = pattern.sub(replacement, result)
    result = re.sub(r"\s{2,}", " ", result).strip()
    if title and result.lower().startswith(title.lower()):
        result = result[len(title):].lstrip(" .:–—-")
    return result


def _span(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 1.0
    low, high = min(values), max(values)
    return (low, high if high - low > 1e-9 else low + 1.0)


def _scaled(value: float, low: float, high: float) -> float:
    return max(0.0, min(1.0, (value - low) / (high - low)))


def candidate_url(candidate: Dict[str, Any], query: str = "") -> str:
    """The reading-view URL for a result, carrying its matched range and the query.

    The range drives the in-page highlight; the query lets the note page offer a way
    back to the results that produced it.
    """
    params: List[Tuple[str, str]] = []
    line_start = candidate.get("line_start") or 0
    if line_start:
        params.append(("from", str(line_start)))
        params.append(("to", str(candidate.get("line_end") or line_start)))
    if query:
        params.append(("q", query))
    url = "/note/" + quote(str(candidate.get("path", "")))
    if params:
        url += "?" + urlencode(params)
    if line_start:
        url += f"#L{line_start}"
    return url


def decorate_candidates(
    candidates: List[Dict[str, Any]], query: str = ""
) -> List[Dict[str, Any]]:
    """Add the display fields the results list needs.

    ``bar`` drives the evidence bar: keyword and semantic strength scaled across this
    result set, which is the only scale on which the two are comparable. It answers
    "why did this surface", not "how good is this in absolute terms".
    """
    bm25_low, bm25_high = _span([float(c["scores"]["bm25"]) for c in candidates])
    sem_low, sem_high = _span([float(c["scores"]["semantic"]) for c in candidates])

    decorated: List[Dict[str, Any]] = []
    for position, candidate in enumerate(candidates, start=1):
        scores = candidate["scores"]
        keyword = _scaled(float(scores["bm25"]), bm25_low, bm25_high)
        semantic = _scaled(float(scores["semantic"]), sem_low, sem_high)
        item = dict(candidate)
        item["position"] = position
        item["excerpt"] = preview(
            str(candidate.get("excerpt", "")), str(candidate.get("title", ""))
        )
        item["url"] = candidate_url(candidate, query)
        item["bar"] = {
            # Percentages of the bar's width, so the two segments always fill it.
            "keyword": round(keyword * 100),
            "semantic": round(semantic * 100),
            "lead": "keyword" if keyword > semantic else "semantic",
            "reranked": scores.get("reranker") is not None,
        }
        item["lines"] = (
            f"L{candidate['line_start']}–{candidate['line_end']}"
            if candidate.get("line_start")
            else ""
        )
        decorated.append(item)
    return decorated


def short_date(value: Any) -> str:
    """A date a person can read, or '' when there isn't one."""
    if not value:
        return ""
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text[:10]
    return parsed.strftime("%-d %b %Y")


def note_masthead(note) -> Dict[str, Any]:
    """The facts shown under a note's title: provenance, type, date, tags."""
    frontmatter = note.frontmatter
    candidates = [
        str(frontmatter.get("provenance") or "").strip().lower(),
        note.note_type,
        short_date(frontmatter.get("updated") or frontmatter.get("created")),
    ]
    # `provenance: distilled` alongside `type: distilled` is common; say it once.
    facts: List[str] = []
    for fact in candidates:
        if fact and fact not in facts:
            facts.append(fact)
    return {
        "facts": facts,
        "tags": [tag.lstrip("#") for tag in note.tags],
        "source_url": str(frontmatter.get("source_url") or "").strip(),
    }


def humanize_error(error_type: str, message: str) -> Dict[str, str]:
    """Turn a contract error type into something worth reading on screen.

    Errors say what happened and what to do next; they do not apologise and they are
    never vague.
    """
    guidance = {
        "index_empty": "Run `./bin/vault-spider sync` to build the index, then reload.",
        "provider_error": "OpenRouter did not answer. Check your key and connection.",
        "not_found": "Nothing in the vault matched. Try different words, or widen the filters.",
        "invalid_arguments": "Adjust the query and try again.",
        "config_mismatch": "Check `vault.root` and `index.chroma_path` in config.yaml.",
    }
    return {
        "type": error_type,
        "message": message,
        "guidance": guidance.get(error_type, ""),
    }


def citation_index(citations: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Citations keyed by their `S0`-style marker, for rewriting them into links."""
    return {str(citation.get("key", "")): dict(citation) for citation in citations}


CITATION_RE = re.compile(r"\[([A-Z]\d+(?:,\s*[A-Z]\d+)*)\]")


def link_citations(answer: str, citations: Sequence[Dict[str, Any]]) -> str:
    """Rewrite `[S0, S1]` markers into Markdown links to the notes they name.

    The path must be percent-encoded: nearly every folder in this vault has a space in
    its name, and a Markdown link destination containing a raw space does not parse — the
    citation would render as literal `[S0](/note/200 Tech/…)` text instead of a link.
    """
    index = citation_index(citations)

    def replace(match: "re.Match[str]") -> str:
        keys = [key.strip() for key in match.group(1).split(",")]
        rendered: List[str] = []
        for key in keys:
            citation = index.get(key)
            path = str(citation.get("path", "")) if citation else ""
            if not path:
                rendered.append(key)
                continue
            rendered.append(f"[{key}](/note/{quote(path)})")
        return "[" + ", ".join(rendered) + "]"

    return CITATION_RE.sub(replace, answer or "")


def first_heading_of(note, line_start: Optional[int]) -> str:
    """The heading a matched line range sits under, for the back-link label."""
    if not line_start:
        return ""
    heading = ""
    for number, line in enumerate(note.body.split("\n"), start=1):
        if number > line_start:
            break
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            heading = match.group(2).strip()
    return heading
