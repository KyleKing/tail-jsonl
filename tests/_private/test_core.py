"""Test core logic.

Generated sample JSONL data with:

```py
from loguru import logger
from calcipy.log_helpers import activate_debug_logging

from tail_jsonl import __pkg_name__

activate_debug_logging(pkg_names=[__pkg_name__])

logger.debug("debug-level log", data={"key1": 123})
logger.info("info-level log")
logger.warning("warning-level log")
logger.error("error-level log")
try:
    1 // 0
except Exception:
    logger.exception("exception-level log")
```

"""

import json
import platform

import pytest
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl.config import Config
from tests.configuration import TEST_DATA_DIR


def read_logs() -> list[str]:
    return (TEST_DATA_DIR / 'logs.jsonl').read_text(encoding='utf-8').strip().split('\n')


LOGS = read_logs()


@pytest.mark.parametrize('logs_index', [*range(len(LOGS))])
def test_core(logs_index, snapshot, console: Console):
    """Smoketest core."""
    print_record(LOGS[logs_index], console, Config())

    result = console.end_capture()

    assert result.strip()
    assert '<no ' not in result
    if platform.system() != 'Windows':
        assert result == snapshot


def test_core_no_key_matches(console: Console):
    print_record('{"key": null}', console, Config())

    result = console.end_capture()

    assert result.strip() == '<no timestamp>               [NOTSET ] <no message> key=None'


def test_core_bad_json(console: Console):
    print_record('{"bad json": None}', console, Config())

    result = console.end_capture()

    assert result.strip() == '{"bad json": None}'


def test_core_logtape_messages(console: Console):
    print_record('{"message": ["LogTape Message"]}', console, Config())

    result = console.end_capture()

    assert result.strip() == "<no timestamp>               [NOTSET ] ['LogTape Message']"


def test_core_wrap(console: Console):
    print_record(json.dumps(dict.fromkeys(range(3), '-' * 3)), console, Config())

    result = console.end_capture()

    if platform.system() != 'Windows':
        expected = '<no timestamp>               [NOTSET ] <no message> 0=--- 1=--- 2=---'
        assert result.strip() == expected


def test_core_error_stack_on_own_line(console: Console):
    line = (
        '{"timestamp":"2025-09-10T15:31:37.651Z","level":"error","category":["app"],'
        '"message":["Failed to load comments"],"host":"localhost:8080","method":"GET","path":"/partials/comments",'
        '"referer":"http://localhost:8080/comments","requestId":"4c58cd34-f521-4af1-8c6d-e61914216710",'
        '"url":"http://localhost:8080/partials/comments","error":{"name":"SourceError","message":"Invalid for loop",'
        '"stack":"SourceError: Invalid for loop\\n    at forTag (https://deno.land/x/vento@v2.0.1/plugins/for.ts:74:11)"},'
        '"request":{"method":"GET","path":"/partials/comments"}}'
    )
    print_record(line, console, Config())
    result = console.end_capture()
    # Should have promoted error.stack out of the error mapping
    assert 'error.stack:' in result or 'error.stack=' in result
    assert 'SourceError: Invalid for loop' in result
    # Original nested stack should not appear inside error={...}
    assert 'stack":' not in result.split('error={')[1] if 'error={' in result else True


# Comprehensive tests for dotted key parsing edge cases (Phase 1)


@pytest.mark.parametrize(
    ('log_data', 'dotted_keys', 'expected_in_output'),
    [
        # Simple nested key
        (
            {'timestamp': '2024-01-01', 'message': 'test', 'server': {'hostname': 'prod-1'}},
            ['server.hostname'],
            'server.hostname',
        ),
        # Deeply nested key
        (
            {'timestamp': '2024-01-01', 'message': 'test', 'app': {'user': {'id': 123}}},
            ['app.user.id'],
            'app.user.id',
        ),
        # Multiple levels of nesting
        (
            {
                'timestamp': '2024-01-01',
                'message': 'test',
                'data': {'request': {'headers': {'user-agent': 'Mozilla'}}},
            },
            ['data.request.headers.user-agent'],
            'data.request.headers.user-agent',
        ),
        # Key that doesn't exist (should not crash)
        (
            {'timestamp': '2024-01-01', 'message': 'test'},
            ['missing.key'],
            'test',  # Should still process the message
        ),
        # Mixed dotted and non-dotted keys
        (
            {
                'timestamp': '2024-01-01',
                'message': 'test',
                'text': 'plain text',
                'server': {'hostname': 'prod-1'},
            },
            ['text', 'server.hostname'],
            'text:',  # Both should appear
        ),
        # String value in nested key
        (
            {'timestamp': '2024-01-01', 'message': 'test', 'error': {'code': 'ERR_500'}},
            ['error.code'],
            'error.code',
        ),
        # Number value in nested key (should be stringified)
        (
            {'timestamp': '2024-01-01', 'message': 'test', 'metrics': {'count': 42}},
            ['metrics.count'],
            'metrics.count',
        ),
        # List value in nested key (should be stringified)
        (
            {'timestamp': '2024-01-01', 'message': 'test', 'tags': {'values': ['a', 'b']}},
            ['tags.values'],
            'tags.values',
        ),
    ],
)
def test_dotted_key_parsing_edge_cases(log_data, dotted_keys, expected_in_output, console: Console):
    """Test dotted key parsing handles various edge cases correctly."""
    from tail_jsonl.config import Config, Keys

    config = Config(keys=Keys(on_own_line=dotted_keys))

    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    assert expected_in_output in result


def test_dotted_key_with_special_chars_in_value(console: Console):
    """Test dotted keys work with special characters in the extracted value."""
    from tail_jsonl.config import Config, Keys

    log_data = {
        'timestamp': '2024-01-01',
        'message': 'test',
        'error': {'stack': 'Error: test\n    at line 1\n    at line 2'},
    }

    config = Config(keys=Keys(on_own_line=['error.stack']))
    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    # Should have promoted error.stack with newlines intact
    assert 'error.stack' in result
    assert 'Error: test' in result


def test_dotted_key_partial_path_exists(console: Console):
    """Test behavior when partial path exists but full path doesn't."""
    from tail_jsonl.config import Config, Keys

    log_data = {
        'timestamp': '2024-01-01',
        'message': 'test',
        'error': {'code': 500},  # error exists, but error.stack doesn't
    }

    config = Config(keys=Keys(on_own_line=['error.stack']))
    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    # Should not crash, error.stack just won't be promoted
    assert 'test' in result
    assert 'error' in result.lower()


def test_dotted_key_non_dict_intermediate(console: Console):
    """Test behavior when intermediate path is not a dict."""
    from tail_jsonl.config import Config, Keys

    log_data = {
        'timestamp': '2024-01-01',
        'message': 'test',
        'error': 'simple string',  # Not a dict, can't have .stack
    }

    config = Config(keys=Keys(on_own_line=['error.stack']))
    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    # Should not crash
    assert 'test' in result


def test_dotted_key_empty_string_key(console: Console):
    """Test behavior with empty string in dotted key (edge case)."""
    from tail_jsonl.config import Config, Keys

    log_data = {
        'timestamp': '2024-01-01',
        'message': 'test',
        'data': 'value',
    }

    # Empty key should be skipped (no '.' in it)
    config = Config(keys=Keys(on_own_line=['']))
    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    # Should not crash, just process normally
    assert 'test' in result


def test_pop_key_fallback_chain():
    """Test the fallback chain in pop_key function."""
    from tail_jsonl._private.core import pop_key

    data = {
        'timestamp': '2024-01-01',
        'record': {'time': {'repr': '2024-01-01T00:00:00'}},
    }

    # Should try 'timestamp' first (exists), return it
    result = pop_key(data, ['timestamp', 'time', 'record.time.repr'], 'fallback')
    assert result == '2024-01-01'
    assert 'timestamp' not in data  # Should be removed

    data = {'record': {'time': {'repr': '2024-01-01T00:00:00'}}}

    # Should try timestamp (missing), time (missing), then record.time.repr (exists via dotted)
    result = pop_key(data, ['timestamp', 'time', 'record.time.repr'], 'fallback')
    assert result == '2024-01-01T00:00:00'

    data = {}

    # All missing, should return fallback
    result = pop_key(data, ['timestamp', 'time'], 'fallback')
    assert result == 'fallback'


def test_pop_key_list_value():
    """Test pop_key converts list values to strings."""
    from tail_jsonl._private.core import pop_key

    data = {'message': ['item1', 'item2']}

    result = pop_key(data, ['message'], 'fallback')
    assert result == "['item1', 'item2']"
    assert 'message' not in data


def test_dotted_key_with_none_value(console: Console):
    """Test dotted key where the value is None."""
    from tail_jsonl.config import Config, Keys

    log_data = {
        'timestamp': '2024-01-01',
        'message': 'test',
        'error': {'code': None},
    }

    config = Config(keys=Keys(on_own_line=['error.code']))
    line = json.dumps(log_data)
    print_record(line, console, config)

    result = console.end_capture()

    # Should process without crashing
    assert 'test' in result
