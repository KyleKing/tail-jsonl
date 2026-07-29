"""Measure end-to-end lines/sec through `print_record` over synthetic JSONL.

Run with `uv run python -m benchmarks.throughput [--lines 10000]`.
"""

from __future__ import annotations

import argparse
import io
import time

from tail_jsonl._private.core import print_record
from tail_jsonl.config import Config

from .records import make_console, simple_line, wide_line

DEFAULT_LINES = 10_000


def generate_lines(count: int) -> list[str]:
    """Return synthetic JSONL alternating simple and wide records."""
    return [wide_line(index) if index % 4 == 0 else simple_line(index) for index in range(count)]


def measure(lines: list[str]) -> float:
    """Return the elapsed seconds to render every line to a discarded buffer."""
    buffer = io.StringIO()
    console = make_console(buffer)
    config = Config()
    start = time.perf_counter()
    for line in lines:
        print_record(line, console, config)
        buffer.seek(0)
        buffer.truncate()
    return time.perf_counter() - start


def main() -> None:
    """Render the generated corpus and report lines/sec."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lines', default=DEFAULT_LINES, type=int)
    parser.add_argument('--repeat', default=3, type=int)
    args = parser.parse_args()

    lines = generate_lines(args.lines)
    durations = [measure(lines) for _ in range(args.repeat)]
    best = min(durations)
    print(f'lines={args.lines} repeat={args.repeat}')
    for index, duration in enumerate(durations):
        print(f'  run {index + 1}: {duration:.3f}s ({args.lines / duration:,.0f} lines/sec)')
    print(f'best: {args.lines / best:,.0f} lines/sec ({best / args.lines * 1e6:.1f} us/line)')


if __name__ == '__main__':
    main()
