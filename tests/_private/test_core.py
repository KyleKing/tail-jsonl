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
from beartype import beartype
from beartype.typing import List
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl.config import Config
from tests.configuration import TEST_DATA_DIR


@beartype
def read_logs() -> List[str]:
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


def test_core_wrap(console: Console):
    print_record(json.dumps(dict.fromkeys(range(3), '-' * 3)), console, Config())

    result = console.end_capture()

    if platform.system() != 'Windows':
        expected = '<no timestamp>               [NOTSET ] <no message> 0=--- 1=--- 2=---'
        assert result.strip() == expected
