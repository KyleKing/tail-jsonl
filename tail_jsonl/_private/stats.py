"""Statistics collection for log processing (Phase 5)."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from time import time

from rich.console import Console

from tail_jsonl._private.core import Record


@dataclass
class Statistics:
    """Collect statistics during log processing."""

    start_time: float = field(default_factory=time)
    total_lines: int = 0
    parsed_lines: int = 0
    parse_errors: int = 0
    filtered_lines: int = 0
    level_counts: Counter[str] = field(default_factory=Counter)
    key_counts: Counter[str] = field(default_factory=Counter)

    def record_line(self, record: Record | None, filtered: bool = False) -> None:
        """Record statistics for a processed line."""
        self.total_lines += 1

        if record is None:
            self.parse_errors += 1
            return

        if filtered:
            self.filtered_lines += 1
            self.parsed_lines += 1  # Still parsed, just filtered
            return

        self.parsed_lines += 1

        # Count level
        if record.level:
            self.level_counts[record.level] += 1

        # Count keys in data
        for key in record.data.keys():
            self.key_counts[key] += 1

    def get_elapsed(self) -> float:
        """Return elapsed time in seconds."""
        return time() - self.start_time

    def get_throughput(self) -> float:
        """Return lines per second."""
        elapsed = self.get_elapsed()
        return self.total_lines / elapsed if elapsed > 0 else 0

    def print_summary(self, console: Console) -> None:
        """Print formatted statistics summary."""
        elapsed = self.get_elapsed()
        throughput = self.get_throughput()

        console.print('\n────────────── Statistics ──────────────', style='bold cyan')
        console.print(f'Processed:     {self.total_lines:,} lines in {elapsed:.1f}s')
        console.print(f'Throughput:    {throughput:,.0f} lines/sec')

        if self.level_counts:
            levels = ', '.join(f'{k}={v:,}' for k, v in self.level_counts.most_common())
            console.print(f'Levels:        {levels}')

        if self.key_counts:
            top_keys = ', '.join(f'{k}={v:,}' for k, v in self.key_counts.most_common(5))
            console.print(f'Top 5 Keys:    {top_keys}')

        if self.parse_errors > 0:
            pct = (self.parse_errors / self.total_lines) * 100 if self.total_lines > 0 else 0
            console.print(f'Parse Errors:  {self.parse_errors:,} lines ({pct:.2f}%)', style='red')

        if self.filtered_lines > 0:
            pct = (self.filtered_lines / self.total_lines) * 100 if self.total_lines > 0 else 0
            console.print(f'Filtered:      {self.filtered_lines:,} lines ({pct:.2f}%)')

    def to_json(self) -> str:
        """Return statistics as JSON string."""
        return json.dumps({
            'total_lines': self.total_lines,
            'parsed_lines': self.parsed_lines,
            'parse_errors': self.parse_errors,
            'filtered_lines': self.filtered_lines,
            'elapsed_seconds': self.get_elapsed(),
            'throughput_lines_per_sec': self.get_throughput(),
            'level_counts': dict(self.level_counts),
            'key_counts': dict(self.key_counts.most_common(10)),
        }, indent=2)
