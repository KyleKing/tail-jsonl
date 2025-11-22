"""Tests for filtering logic (Phase 3 - Stern-Aligned)."""

from __future__ import annotations

import re

import pytest
from rich.console import Console

from tail_jsonl._private.core import Record
from tail_jsonl._private.filters import _get_field_value, should_include_record
from tail_jsonl.config import Config


# Test fixtures and helpers

def make_record(
    timestamp: str = '2024-01-01T00:00:00',
    level: str = 'INFO',
    message: str = 'test message',
    **data: str | int | dict,  # type: ignore[type-arg]
) -> Record:
    """Create a test Record."""
    return Record(
        timestamp=timestamp,
        level=level,
        message=message,
        data=dict(data),
    )


# Include/Exclude regex tests


@pytest.mark.parametrize(
    ('formatted_output', 'include', 'exclude', 'expected'),
    [
        # Include pattern tests
        ('ERROR: failed', 'error', None, True),  # Case insensitive match
        ('ERROR: failed', 'ERROR', None, True),  # Exact case match
        ('INFO: ok', 'error', None, False),  # No match
        ('error warning debug', 'error|warning', None, True),  # Regex OR
        # Exclude pattern tests
        ('DEBUG: trace', None, 'DEBUG|TRACE', False),  # Exclude match
        ('INFO: message', None, 'DEBUG|TRACE', True),  # No exclude match
        # Combined include + exclude
        ('ERROR: test', 'error', None, True),  # Include only
        ('ERROR: test', 'error', 'test', False),  # Exclude takes precedence
        ('ERROR: production', 'error', 'test', True),  # Include matches, exclude doesn't
        ('INFO: test', 'error', 'test', False),  # Include doesn't match
        # Edge cases
        ('', 'error', None, False),  # Empty output, include
        ('', None, 'error', True),  # Empty output, exclude
        ('ERROR', 'error', 'error', False),  # Both match, exclude wins
    ],
)
def test_include_exclude_filter(formatted_output: str, include: str | None, exclude: str | None, expected: bool):
    """Test include/exclude regex filtering on formatted output."""
    record = make_record()
    config = Config(
        include_pattern=include,
        exclude_pattern=exclude,
        case_insensitive=True,  # Case insensitive by default
    )

    result = should_include_record(record, formatted_output, config)

    assert result == expected


@pytest.mark.parametrize(
    ('formatted_output', 'pattern', 'case_sensitive', 'expected'),
    [
        # Case sensitivity tests
        ('ERROR', 'error', False, True),  # Case insensitive
        ('ERROR', 'error', True, False),  # Case sensitive, no match
        ('error', 'error', True, True),  # Case sensitive, exact match
        ('Error', 'error', False, True),  # Case insensitive
        ('Error', 'error', True, False),  # Case sensitive, no match
    ],
)
def test_case_sensitivity(formatted_output: str, pattern: str, case_sensitive: bool, expected: bool):
    """Test case-sensitive vs case-insensitive regex matching."""
    record = make_record()
    config = Config(
        include_pattern=pattern,
        case_insensitive=not case_sensitive,  # Inverted logic
    )

    result = should_include_record(record, formatted_output, config)

    assert result == expected


# Field selector tests


@pytest.mark.parametrize(
    ('record_data', 'selector', 'expected'),
    [
        # Simple field selectors
        ({'level': 'error'}, ('level', 'error'), True),
        ({'level': 'info'}, ('level', 'error'), False),
        ({'level': 'ERROR'}, ('level', 'error'), True),  # Case insensitive
        # Glob patterns
        ({'host': 'prod-1'}, ('host', 'prod-*'), True),
        ({'host': 'prod-2'}, ('host', 'prod-*'), True),
        ({'host': 'dev-1'}, ('host', 'prod-*'), False),
        ({'env': 'production'}, ('env', 'prod*'), True),
        ({'env': 'staging'}, ('env', 'prod*'), False),
        # Exact match
        ({'status': 'success'}, ('status', 'success'), True),
        ({'status': 'failure'}, ('status', 'success'), False),
    ],
)
def test_field_selector_simple(record_data: dict[str, str], selector: tuple[str, str], expected: bool):  # type: ignore[type-arg]
    """Test simple field selector filtering."""
    record = make_record(**record_data)
    config = Config(field_selectors=[selector])

    result = should_include_record(record, 'formatted output', config)

    assert result == expected


@pytest.mark.parametrize(
    ('record_kwargs', 'selector', 'expected'),
    [
        # Standard extracted fields
        ({'timestamp': '2024-01-01'}, ('timestamp', '2024-01-01'), True),
        ({'timestamp': '2024-01-01'}, ('timestamp', '2024-*'), True),
        ({'timestamp': '2023-12-31'}, ('timestamp', '2024-*'), False),
        ({'level': 'ERROR'}, ('level', 'error'), True),  # Case insensitive
        ({'level': 'INFO'}, ('level', 'error'), False),
        ({'message': 'payment processed'}, ('message', 'payment*'), True),
        ({'message': 'user login'}, ('message', 'payment*'), False),
    ],
)
def test_field_selector_standard_fields(record_kwargs: dict[str, str], selector: tuple[str, str], expected: bool):  # type: ignore[type-arg]
    """Test field selectors on standard extracted fields (timestamp, level, message)."""
    record = make_record(**record_kwargs)
    config = Config(field_selectors=[selector])

    result = should_include_record(record, 'formatted output', config)

    assert result == expected


@pytest.mark.parametrize(
    ('record_data', 'selector', 'expected'),
    [
        # Dotted key selectors
        ({'server': {'hostname': 'prod-1'}}, ('server.hostname', 'prod-1'), True),
        ({'server': {'hostname': 'prod-1'}}, ('server.hostname', 'prod-*'), True),
        ({'server': {'hostname': 'dev-1'}}, ('server.hostname', 'prod-*'), False),
        # Deeply nested
        ({'app': {'user': {'id': '123'}}}, ('app.user.id', '123'), True),
        ({'app': {'user': {'id': '456'}}}, ('app.user.id', '123'), False),
        # Multiple levels
        (
            {'data': {'request': {'headers': {'user-agent': 'Mozilla'}}}},
            ('data.request.headers.user-agent', 'Mozilla*'),
            True,
        ),
        (
            {'data': {'request': {'headers': {'user-agent': 'Chrome'}}}},
            ('data.request.headers.user-agent', 'Mozilla*'),
            False,
        ),
    ],
)
def test_field_selector_dotted_keys(record_data: dict[str, str | dict], selector: tuple[str, str], expected: bool):  # type: ignore[type-arg]
    """Test field selectors with dotted keys for nested data."""
    record = make_record(**record_data)
    config = Config(field_selectors=[selector])

    result = should_include_record(record, 'formatted output', config)

    assert result == expected


def test_field_selector_multiple_and_logic():
    """Test multiple field selectors with AND logic."""
    record = make_record(
        level='ERROR',
        host='prod-1',
        env='production',
    )

    # All match - should pass
    config = Config(field_selectors=[
        ('level', 'error'),
        ('host', 'prod-*'),
        ('env', 'prod*'),
    ])
    assert should_include_record(record, 'formatted', config) is True

    # One doesn't match - should fail
    config = Config(field_selectors=[
        ('level', 'error'),
        ('host', 'dev-*'),  # Doesn't match
        ('env', 'prod*'),
    ])
    assert should_include_record(record, 'formatted', config) is False


def test_field_selector_missing_key():
    """Test field selector when key doesn't exist in record."""
    record = make_record(host='prod-1')

    # Key exists
    config = Config(field_selectors=[('host', 'prod-*')])
    assert should_include_record(record, 'formatted', config) is True

    # Key doesn't exist
    config = Config(field_selectors=[('missing_key', 'value')])
    assert should_include_record(record, 'formatted', config) is False


def test_field_selector_partial_dotted_path():
    """Test field selector when partial dotted path exists but full path doesn't."""
    record = make_record(error={'code': 500})  # error exists, but error.stack doesn't

    # Partial path exists, full path doesn't
    config = Config(field_selectors=[('error.stack', '*')])
    assert should_include_record(record, 'formatted', config) is False


def test_field_selector_non_dict_intermediate():
    """Test field selector when intermediate path is not a dict."""
    record = make_record(error='simple string')  # Not a dict, can't have .stack

    config = Config(field_selectors=[('error.stack', '*')])
    assert should_include_record(record, 'formatted', config) is False


# Integration tests


def test_combined_filters():
    """Test combining field selectors, include, and exclude patterns."""
    record = make_record(
        level='ERROR',
        message='payment failed',
        host='prod-1',
    )
    formatted = 'ERROR: payment failed host=prod-1'

    # All filters pass
    config = Config(
        include_pattern='payment',
        exclude_pattern='test',
        field_selectors=[('level', 'error'), ('host', 'prod-*')],
        case_insensitive=True,
    )
    assert should_include_record(record, formatted, config) is True

    # Include pattern fails
    config = Config(
        include_pattern='success',
        field_selectors=[('level', 'error')],
        case_insensitive=True,
    )
    assert should_include_record(record, formatted, config) is False

    # Exclude pattern matches
    config = Config(
        include_pattern='payment',
        exclude_pattern='failed',
        field_selectors=[('level', 'error')],
        case_insensitive=True,
    )
    assert should_include_record(record, formatted, config) is False

    # Field selector fails
    config = Config(
        include_pattern='payment',
        field_selectors=[('level', 'info')],  # Doesn't match ERROR
        case_insensitive=True,
    )
    assert should_include_record(record, formatted, config) is False


def test_no_filters():
    """Test that record passes when no filters are configured."""
    record = make_record()
    config = Config()

    assert should_include_record(record, 'formatted output', config) is True


# Edge cases


def test_invalid_regex_pattern():
    """Test that invalid regex patterns raise errors during config initialization."""
    with pytest.raises(re.error):
        Config(include_pattern='[invalid(')


def test_empty_patterns():
    """Test behavior with empty patterns."""
    record = make_record()

    # Empty include pattern - treated as no pattern since empty string is falsy
    config = Config(include_pattern='', case_insensitive=True)
    # Since empty string is falsy, _include_re is not set, so should pass
    assert should_include_record(record, 'output', config) is True

    # Empty exclude pattern - treated as no pattern since empty string is falsy
    config = Config(exclude_pattern='', case_insensitive=True)
    # Since empty string is falsy, _exclude_re is not set, so should pass
    assert should_include_record(record, 'output', config) is True


# Helper function tests


@pytest.mark.parametrize(
    ('record', 'key', 'expected'),
    [
        # Standard fields
        (make_record(timestamp='2024-01-01'), 'timestamp', '2024-01-01'),
        (make_record(level='ERROR'), 'level', 'ERROR'),
        (make_record(message='test'), 'message', 'test'),
        # Data fields
        (make_record(host='prod-1'), 'host', 'prod-1'),
        (make_record(count=42), 'count', '42'),  # Number converted to string
        # Dotted keys
        (make_record(server={'hostname': 'prod-1'}), 'server.hostname', 'prod-1'),
        (make_record(app={'user': {'id': 123}}), 'app.user.id', '123'),
        # Missing keys
        (make_record(), 'missing', None),
        (make_record(error={'code': 500}), 'error.stack', None),
    ],
)
def test_get_field_value(record: Record, key: str, expected: str | None):
    """Test _get_field_value helper function."""
    result = _get_field_value(record, key)

    assert result == expected
