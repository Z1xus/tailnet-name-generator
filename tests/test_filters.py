"""Tests for filter logic."""

import pytest

from ts_name.filters import FilterConfig
from ts_name.filters import FilterOperator
from ts_name.filters import create_filter


class TestFilterConfig:
    """Tests for FilterConfig dataclass."""

    def test_basic_and_filter(self) -> None:
        """Test AND operator with multiple words."""
        config = FilterConfig(
            words=["king", "ratio"],
            operator=FilterOperator.AND,
        )
        assert config.matches("king-ratio")
        assert not config.matches("king-hen")
        assert not config.matches("great-ratio")

    def test_basic_or_filter(self) -> None:
        """Test OR operator with multiple words."""
        config = FilterConfig(
            words=["king", "ratio"],
            operator=FilterOperator.OR,
        )
        assert config.matches("king-ratio")
        assert config.matches("king-hen")
        assert config.matches("great-ratio")
        assert not config.matches("great-hen")

    def test_max_length_filter(self) -> None:
        """Test maximum length filtering."""
        config = FilterConfig(words=[], max_length=10)
        assert config.matches("short")
        assert config.matches("tencharnam")  # 10 chars exactly
        assert not config.matches("toolongname")  # 11 chars

    def test_min_length_filter(self) -> None:
        """Test minimum length filtering."""
        config = FilterConfig(words=[], min_length=5)
        assert not config.matches("tiny")
        assert config.matches("quite")
        assert config.matches("longername")

    def test_combined_length_filter(self) -> None:
        """Test both min and max length together."""
        config = FilterConfig(
            words=[],
            min_length=3,
            max_length=8,
        )
        assert not config.matches("ab")
        assert config.matches("abc")
        assert config.matches("abcdefgh")
        assert not config.matches("abcdefghi")

    def test_invalid_length_range(self) -> None:
        """Test that invalid length range raises error."""
        with pytest.raises(ValueError, match="min_length"):
            FilterConfig(words=[], min_length=10, max_length=5)

    def test_case_insensitive_matching(self) -> None:
        """Test that word matching is case-insensitive."""
        config = FilterConfig(words=["King"], operator=FilterOperator.AND)
        assert config.matches("king-ratio")
        assert config.matches("KING-RATIO")
        assert config.matches("King-Ratio")

    def test_empty_words_list(self) -> None:
        """Test that empty words list matches everything (except length filters)."""
        config = FilterConfig(words=[])
        assert config.matches("anything")
        assert config.matches("xyz")

    def test_partial_word_match(self) -> None:
        """Test that partial word matches work."""
        config = FilterConfig(words=["yo"], operator=FilterOperator.OR)
        assert config.matches("yogi-bear")
        assert config.matches("king-yo")
        assert config.matches("yo-yo")


class TestCreateFilter:
    """Tests for create_filter helper function."""

    def test_create_filter_and(self) -> None:
        """Test creating an AND filter."""
        filter_fn = create_filter(
            words=["king", "ratio"],
            operator=FilterOperator.AND,
        )
        assert filter_fn("king-ratio")
        assert not filter_fn("king-hen")

    def test_create_filter_or(self) -> None:
        """Test creating an OR filter."""
        filter_fn = create_filter(
            words=["king", "ratio"],
            operator=FilterOperator.OR,
        )
        assert filter_fn("king-ratio")
        assert filter_fn("king-hen")
        assert filter_fn("great-ratio")

    def test_create_filter_with_length(self) -> None:
        """Test creating a filter with length constraints."""
        filter_fn = create_filter(max_length=8)
        assert filter_fn("short")
        assert not filter_fn("verylongname")

    def test_create_filter_none_words(self) -> None:
        """Test creating a filter with None words."""
        filter_fn = create_filter(words=None)
        assert filter_fn("anything")

    def test_create_filter_all_options(self) -> None:
        """Test creating a filter with all options."""
        filter_fn = create_filter(
            words=["king"],
            min_length=4,
            max_length=12,
            operator=FilterOperator.AND,
        )
        assert filter_fn("king-n")  # 6 chars, contains king
        assert not filter_fn("kin")  # 3 chars, too short
        assert not filter_fn("king-verylongname")  # too long
        assert not filter_fn("great-ratio")  # doesn't contain king
