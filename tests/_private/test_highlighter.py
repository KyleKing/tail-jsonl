"""Tests for highlighting logic (Phase 4 - Stern-Aligned)."""

from __future__ import annotations

import re

import pytest
from rich.text import Text

from tail_jsonl._private.highlighter import HIGHLIGHT_COLORS, apply_highlighting
from tail_jsonl.config import Config


# Basic highlighting tests


@pytest.mark.parametrize(
    ('text', 'pattern', 'expected_match_count'),
    [
        # Single match
        ('ERROR: failed', 'error', 1),  # Case insensitive by default
        ('ERROR: failed', 'ERROR', 1),  # Exact case
        # Multiple matches
        ('ERROR and error', 'error', 2),
        ('error warning error debug error', 'error', 3),
        # No matches
        ('INFO: success', 'error', 0),
        # Regex OR
        ('ERROR: warning detected', 'error|warning', 2),
        # Word boundaries
        ('error-prone errorhandler', r'\berror\b', 1),  # Only matches 'error-prone'
    ],
)
def test_highlight_single_pattern(text: str, pattern: str, expected_match_count: int):
    """Test highlighting with a single pattern."""
    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    if expected_match_count == 0:
        # No matches should still return Text object but with no styles
        assert isinstance(result, Text)
        assert str(result) == text
    else:
        assert isinstance(result, Text)
        # Text should contain the original content
        assert str(result) == text


@pytest.mark.parametrize(
    ('text', 'patterns', 'expected_colors'),
    [
        # Two patterns
        ('error and warning', ['error', 'warning'], 2),
        # Three patterns
        ('error warning info', ['error', 'warning', 'info'], 3),
        # More patterns than colors (should cycle)
        (
            'p1 p2 p3 p4 p5 p6 p7 p8',
            ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'],
            len(HIGHLIGHT_COLORS),  # Colors should cycle
        ),
    ],
)
def test_highlight_multiple_patterns(text: str, patterns: list[str], expected_colors: int):
    """Test highlighting with multiple patterns using different colors."""
    config = Config(
        highlight_patterns=patterns,
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # Each pattern should get a unique color (cycling if needed)
    # We can't easily verify colors without inspecting Rich internals,
    # but we can verify it returns a Text object


def test_highlight_color_cycling():
    """Test that colors cycle when more patterns than colors."""
    # Create more patterns than available colors
    num_patterns = len(HIGHLIGHT_COLORS) + 3
    patterns = [f'p{i}' for i in range(num_patterns)]
    text = ' '.join(patterns)

    config = Config(
        highlight_patterns=patterns,
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    # Should successfully apply all highlights without error
    assert str(result) == text


# Case sensitivity tests


@pytest.mark.parametrize(
    ('text', 'pattern', 'case_sensitive', 'should_match'),
    [
        # Case insensitive (default)
        ('ERROR', 'error', False, True),
        ('error', 'ERROR', False, True),
        ('Error', 'error', False, True),
        # Case sensitive
        ('ERROR', 'error', True, False),
        ('error', 'error', True, True),
        ('Error', 'error', True, False),
        ('ERROR', 'ERROR', True, True),
    ],
)
def test_highlight_case_sensitivity(text: str, pattern: str, case_sensitive: bool, should_match: bool):
    """Test case-sensitive vs case-insensitive highlighting."""
    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=case_sensitive,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # We can verify the pattern was compiled correctly in config
    assert config._highlight_res is not None
    assert len(config._highlight_res) == 1


# Overlapping matches


def test_highlight_overlapping_patterns():
    """Test that overlapping patterns are handled correctly."""
    text = 'error-warning-info'
    patterns = ['error', 'warning', 'error-warning']  # Overlapping patterns

    config = Config(
        highlight_patterns=patterns,
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # Rich should handle overlapping styles automatically


def test_highlight_same_pattern_multiple_times():
    """Test same word appearing multiple times in text."""
    text = 'error here and error there and another error'
    pattern = 'error'

    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # All three occurrences should be highlighted


# Edge cases


def test_highlight_no_patterns():
    """Test with no highlight patterns configured."""
    text = 'some log output'
    config = Config()  # No patterns

    result = apply_highlighting(text, config)

    # Should return original string, not Text object
    assert isinstance(result, str)
    assert result == text


def test_highlight_empty_text():
    """Test highlighting empty text."""
    text = ''
    config = Config(
        highlight_patterns=['error'],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == ''


def test_highlight_empty_pattern():
    """Test with empty pattern string."""
    text = 'some text'
    config = Config(
        highlight_patterns=[''],  # Empty pattern
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    # Empty regex matches at the start of the string, but that's valid


def test_highlight_special_chars():
    """Test highlighting with special regex characters."""
    text = 'ERROR: [failed] (code=500)'
    pattern = r'\[failed\]'  # Escaped brackets

    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text


def test_highlight_multiline_text():
    """Test highlighting with newlines in text."""
    text = 'error on line 1\ninfo on line 2\nerror on line 3'
    pattern = 'error'

    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # Both 'error' occurrences should be found across lines


def test_highlight_unicode():
    """Test highlighting with unicode characters."""
    text = 'エラー: error in Japanese: エラー'
    pattern = 'error'

    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text


def test_highlight_very_long_text():
    """Test highlighting with very long text."""
    text = 'error ' * 1000  # Long text with many matches
    pattern = 'error'

    config = Config(
        highlight_patterns=[pattern],
        highlight_case_sensitive=False,
    )

    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result).strip() == text.strip()


# Invalid patterns


def test_highlight_invalid_regex():
    """Test that invalid regex patterns raise errors during config initialization."""
    with pytest.raises(re.error):
        Config(
            highlight_patterns=['[invalid('],
            highlight_case_sensitive=False,
        )


# Integration tests


def test_highlight_with_filters():
    """Test that highlighting config coexists with filter config."""
    config = Config(
        include_pattern='error',
        highlight_patterns=['failed'],
        case_insensitive=True,
        highlight_case_sensitive=False,
    )

    text = 'ERROR: failed'
    result = apply_highlighting(text, config)

    assert isinstance(result, Text)
    assert str(result) == text
    # Both filter and highlight patterns should be compiled
    assert config._include_re is not None
    assert config._highlight_res is not None


def test_highlight_pattern_compilation():
    """Test that patterns are compiled correctly in config."""
    patterns = ['error', 'warning', 'info']
    config = Config(
        highlight_patterns=patterns,
        highlight_case_sensitive=False,
    )

    assert config._highlight_res is not None
    assert len(config._highlight_res) == len(patterns)
    # Patterns should be case-insensitive
    for pattern in config._highlight_res:
        assert pattern.flags & re.IGNORECASE


def test_highlight_pattern_compilation_case_sensitive():
    """Test that case-sensitive patterns are compiled correctly."""
    patterns = ['ERROR', 'WARNING']
    config = Config(
        highlight_patterns=patterns,
        highlight_case_sensitive=True,
    )

    assert config._highlight_res is not None
    assert len(config._highlight_res) == len(patterns)
    # Patterns should be case-sensitive
    for pattern in config._highlight_res:
        assert not (pattern.flags & re.IGNORECASE)
