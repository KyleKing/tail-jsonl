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


@pytest.mark.parametrize(
    ('level', 'expected'),
    [
        ('critical', '[CRITICL]'),
        ('fatal', '[FATAL  ]'),
        ('trace', '[TRACE  ]'),
        ('notice', '[NOTICE ]'),
        ('warn', '[WARN   ]'),
        ('Error', '[ERROR  ]'),
        ('emergency', '[EMERGEY]'),
    ],
)
def test_core_renders_the_emitted_level_name(level, expected, console: Console):
    print_record(json.dumps({'level': level, 'message': 'hi'}), console, Config())

    result = console.end_capture()

    assert expected in result
    assert '_level_name' not in result


def test_core_critical_does_not_raise(console: Console):
    """Rich only builds a traceback inside an `except:` block."""
    print_record('{"level":"critical","message":"boom"}', console, Config())

    assert 'boom' in console.end_capture()


def test_core_renders_a_numeric_level(console: Console):
    """A bare number carries no severity, because pino and `logging` disagree on the scale."""
    print_record('{"level":30,"msg":"served"}', console, Config())

    result = console.end_capture()

    assert '[30     ] served' in result
    assert 'level=' not in result


@pytest.mark.parametrize(
    ('line', 'expected'),
    [
        ('{"message":42}', '42'),
        ('{"message":1.5}', '1.5'),
        ('{"message":true}', 'True'),
        ('{"message":0}', '0'),
    ],
)
def test_core_renders_numeric_slot_values(line, expected, console: Console):
    print_record(line, console, Config())

    result = console.end_capture()

    assert expected in result
    assert 'no message' not in result


def test_core_pino_renders_without_configuration(console: Console):
    print_record('{"level":30,"time":1709296245123,"msg":"request served","pid":1}', console, Config())

    result = console.end_capture()

    assert result.startswith('2024-03-01T12:30:45.123')
    assert '[30     ] request served' in result
    assert 'pid=1' in result


def test_core_nested_extraction_prunes_the_parent(console: Console):
    """`record.time.repr` is a default timestamp key, so its containers should not linger."""
    line = '{"record":{"time":{"repr":"2024-03-01T12:30:45Z"}},"message":"hi"}'
    print_record(line, console, Config())

    result = console.end_capture()

    assert result.startswith('2024-03-01T12:30:45Z')
    assert 'record=' not in result


def test_core_promotion_prunes_the_emptied_parent(console: Console):
    print_record('{"level":"error","message":"boom","error":{"stack":"Traceback"}}', console, Config())

    result = console.end_capture()

    assert 'Traceback' in result
    assert 'error={}' not in result


def test_core_bad_json(console: Console):
    print_record('{"bad json": None}', console, Config())

    result = console.end_capture()

    assert result.strip() == '{"bad json": None}'


@pytest.mark.parametrize('line', ['[1, 2]', '"hello"', '42', 'true', 'null'])
def test_core_non_object_json(line, console: Console):
    print_record(line, console, Config())

    result = console.end_capture()

    assert result.strip() == line


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
