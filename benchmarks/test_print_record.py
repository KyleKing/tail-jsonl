"""Per-line rendering benchmarks for `print_record`."""

from __future__ import annotations

import io
from collections.abc import Callable
from typing import TYPE_CHECKING

from tail_jsonl._private.core import print_record
from tail_jsonl.config import Config

from .records import make_console, simple_line, wide_line

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture


def _renderer(line: str) -> Callable[[], None]:
    """Return a zero-argument callable that renders `line` and discards the output."""
    buffer = io.StringIO()
    console = make_console(buffer)
    config = Config()

    def render() -> None:
        print_record(line, console, config)
        buffer.seek(0)
        buffer.truncate()

    return render


def test_print_record_simple(benchmark: BenchmarkFixture) -> None:
    """Time a minimal record: timestamp, level, message, and two extra keys."""
    benchmark(_renderer(simple_line()))


def test_print_record_wide(benchmark: BenchmarkFixture) -> None:
    """Time a 20+ key nested record that promotes `error.stack` onto its own line."""
    benchmark(_renderer(wide_line()))
