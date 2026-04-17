"""Tests for pure helpers in utils.py."""

from __future__ import annotations

from nltk.stem import PorterStemmer

from utils import (
    DEFAULT_STOP_WORDS,
    decimal_to_base,
    hash_string,
    normalize_no_punct,
    tokenize_for_bm25,
)


class TestDecimalToBase:
    def test_zero(self):
        assert decimal_to_base(0) == "0"

    def test_base62_roundtrip_is_alphanumeric(self):
        result = decimal_to_base(123456789)
        assert result.isalnum()

    def test_distinct_inputs_give_distinct_outputs(self):
        assert decimal_to_base(1) != decimal_to_base(2)


class TestHashString:
    def test_deterministic(self):
        assert hash_string("hello") == hash_string("hello")

    def test_different_inputs_produce_different_hashes(self):
        assert hash_string("a") != hash_string("b")

    def test_returns_non_empty_string(self):
        assert hash_string("anything")


class TestNormalizeNoPunct:
    def test_lowercases_and_strips_punctuation(self):
        assert normalize_no_punct("Hello, World!") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize_no_punct("a  b\tc\nd") == "a b c d"

    def test_empty(self):
        assert normalize_no_punct("") == ""


class TestTokenizeForBm25:
    def test_removes_stop_words_and_stems(self):
        stemmer = PorterStemmer()
        tokens = tokenize_for_bm25(
            "The running dogs are jumping.", DEFAULT_STOP_WORDS, stemmer
        )
        # "the" and "are" are stop words; "running" -> "run", "jumping" -> "jump".
        assert "the" not in tokens
        assert "are" not in tokens
        assert "run" in tokens
        assert "jump" in tokens

    def test_lowercases(self):
        stemmer = PorterStemmer()
        tokens = tokenize_for_bm25("Dogs", set(), stemmer)
        assert tokens == [stemmer.stem("dogs")]
