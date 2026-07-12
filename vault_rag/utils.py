"""Pure text/hashing helpers shared across the package."""

from __future__ import annotations

import ctypes
import hashlib
import re
import string
from typing import Iterable, List

WORD_RE = r"\b\w+\b"

# Small built-in list so the app does not depend on downloading NLTK corpora.
DEFAULT_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}

conversion_d = {
    idx: value for value, idx in zip(string.digits + string.ascii_letters, range(62))
}


def decimal_to_base(n: int) -> str:
    if n == 0:
        return "0"

    digits = []
    while n:
        digits.append(int(n % 62))
        n //= 62

    return "".join(conversion_d[x] for x in reversed(digits))


def hash_string(value: str) -> str:
    return decimal_to_base(
        ctypes.c_uint64(int(hashlib.md5(value.encode("utf-8")).hexdigest(), 16)).value
    )


def normalize_no_punct(text: str) -> str:
    return " ".join(re.findall(WORD_RE, text.lower()))


def tokenize_for_bm25(text: str, stop_words: Iterable[str], stemmer) -> List[str]:
    tokens = re.findall(WORD_RE, text.lower())
    return [stemmer.stem(token) for token in tokens if token and token not in stop_words]
