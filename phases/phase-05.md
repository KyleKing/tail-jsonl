# Phase 5: Statistics & Metrics Summary

**Priority:** MEDIUM
**External Dependencies:** None (uses stdlib only)
**Estimated Complexity:** Low-Medium

## Objectives

Provide summary statistics after log processing to give users quick insights into log characteristics, identify parsing issues, and validate log quality.

## Features

### 4.4 Statistics/Metrics Summary

**Goal:** Display summary statistics after processing logs

**Example Output:**
```bash
$ tail-jsonl --stats < logs.jsonl

# ... formatted log output ...

────────────── Statistics ──────────────
Processed:     10,000 lines in 2.3s
Throughput:    4,347 lines/sec
Levels:        ERROR=45, WARNING=123, INFO=9,832
Top 5 Keys:    timestamp=10,000, message=10,000, user_id=8,234,
               request_id=7,891, host=10,000
Parse Errors:  12 lines (0.12%)
Filtered:      234 lines (2.34%)
```

**Proposed Flags:**

```bash
tail-jsonl --stats                    # Show summary at end
tail-jsonl --stats --stats-only       # Only show stats, suppress output
tail-jsonl --stats --stats-json       # Output stats as JSON
```

**Implementation Plan:**

1. **Add Statistics collector class:**
   ```python
   # tail_jsonl/_private/stats.py
   from dataclasses import dataclass, field
   from collections import Counter
   from time import time

   @dataclass
   class Statistics:
       """Collect statistics during log processing."""
       start_time: float = field(default_factory=time)
       total_lines: int = 0
       parsed_lines: int = 0
       parse_errors: int = 0
       filtered_lines: int = 0
       level_counts: Counter = field(default_factory=Counter)
       key_counts: Counter = field(default_factory=Counter)

       def record_line(self, record: Record | None, filtered: bool = False):
           """Record statistics for a processed line."""
           self.total_lines += 1

           if record is None:
               self.parse_errors += 1
               return

           if filtered:
               self.filtered_lines += 1
               return

           self.parsed_lines += 1

           # Count level
           if record.level:
               self.level_counts[record.level] += 1

           # Count keys
           for key in record.data.keys():
               self.key_counts[key] += 1

       def get_summary(self) -> dict:
           """Get summary statistics."""
           elapsed = time() - self.start_time
           throughput = self.total_lines / elapsed if elapsed > 0 else 0

           return {
               'total_lines': self.total_lines,
               'parsed_lines': self.parsed_lines,
               'parse_errors': self.parse_errors,
               'filtered_lines': self.filtered_lines,
               'elapsed_seconds': elapsed,
               'throughput_lines_per_sec': throughput,
               'level_counts': dict(self.level_counts),
               'top_keys': dict(self.key_counts.most_common(5)),
           }

       def print_summary(self, console: Console):
           """Print formatted summary to console."""
           summary = self.get_summary()

           console.print("\n[bold]────────────── Statistics ──────────────[/bold]")

           # Processing stats
           console.print(
               f"Processed:     {summary['total_lines']:,} lines in {summary['elapsed_seconds']:.1f}s"
           )
           console.print(
               f"Throughput:    {summary['throughput_lines_per_sec']:,.0f} lines/sec"
           )

           # Level counts
           if summary['level_counts']:
               levels = ', '.join(
                   f"{level}={count:,}"
                   for level, count in sorted(summary['level_counts'].items())
               )
               console.print(f"Levels:        {levels}")

           # Top keys
           if summary['top_keys']:
               keys = ', '.join(
                   f"{key}={count:,}"
                   for key, count in summary['top_keys'].items()
               )
               console.print(f"Top 5 Keys:    {keys}")

           # Errors
           if summary['parse_errors'] > 0:
               pct = (summary['parse_errors'] / summary['total_lines']) * 100
               console.print(
                   f"[yellow]Parse Errors:  {summary['parse_errors']:,} lines ({pct:.2f}%)[/yellow]"
               )

           # Filtered
           if summary['filtered_lines'] > 0:
               pct = (summary['filtered_lines'] / summary['total_lines']) * 100
               console.print(
                   f"Filtered:      {summary['filtered_lines']:,} lines ({pct:.2f}%)"
               )
   ```

2. **Add config fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       show_stats: bool = False
       stats_only: bool = False  # Suppress log output
       stats_json: bool = False  # Output stats as JSON
   ```

3. **Add CLI flags:**
   ```python
   @invoke.task(
       help={
           'stats': 'Show summary statistics after processing',
           'stats-only': 'Only show statistics, suppress log output',
           'stats-json': 'Output statistics as JSON to stderr',
       }
   )
   def main(ctx, stats=False, stats_only=False, stats_json=False, ...):
   ```

4. **Integrate into main loop:**
   ```python
   def process_logs(console: Console, config: Config):
       """Process logs with optional statistics collection."""
       stats = Statistics() if config.show_stats else None

       with fileinput.input() as _f:
           for line in _f:
               record = parse_record(line)

               # Track statistics
               if stats:
                   filtered = not should_include_record(record, config)
                   stats.record_line(record, filtered=filtered)

               # Skip if stats-only mode
               if config.stats_only:
                   continue

               # Normal processing
               if record and should_include_record(record, config):
                   print_record_formatted(record, console, config)

       # Print statistics summary
       if stats:
           if config.stats_json:
               import json
               import sys
               json.dump(stats.get_summary(), sys.stderr)
               sys.stderr.write('\n')
           else:
               stats.print_summary(console)
   ```

5. **Handle edge cases:**
   - Division by zero for throughput
   - No logs processed (empty input)
   - Large numbers formatting (use commas)
   - Stats to stderr vs stdout (avoid mixing with log output)

**Acceptance Criteria:**
- [ ] `--stats` shows summary after processing
- [ ] `--stats-only` suppresses log output
- [ ] `--stats-json` outputs JSON to stderr
- [ ] Summary includes: lines, throughput, levels, top keys, errors, filtered
- [ ] Statistics don't slow down processing (<2% overhead)
- [ ] Empty input handled gracefully
- [ ] Large numbers formatted with commas
- [ ] Comprehensive unit tests
- [ ] Integration tests with real logs
- [ ] Documentation with examples

## Testing Strategy

**Approach:** TDD with synthetic log data

1. **Statistics collection tests:**
   ```python
   def test_statistics_basic():
       stats = Statistics()
       record1 = Record(level='error', data={'key1': 'value'})
       record2 = Record(level='info', data={'key1': 'value', 'key2': 'value'})

       stats.record_line(record1, filtered=False)
       stats.record_line(record2, filtered=False)

       summary = stats.get_summary()
       assert summary['total_lines'] == 2
       assert summary['level_counts'] == {'error': 1, 'info': 1}
       assert summary['top_keys'] == {'key1': 2, 'key2': 1}
   ```

2. **Edge case tests:**
   - Empty input (0 lines)
   - All parse errors
   - All filtered
   - Very large numbers
   - Division by zero (instant processing)

3. **Format tests:**
   - Text output format
   - JSON output format
   - Consistent formatting with Rich

4. **Integration tests:**
   - Process real logs with --stats
   - Verify stats accuracy
   - Check stats-only mode
   - Validate JSON output

5. **Performance tests:**
   - Statistics overhead <2%
   - Memory usage acceptable (Counter memory)
   - No impact on main processing loop

## Performance Considerations

- **Counter overhead:** Python's Counter is fast, but verify overhead is minimal
- **Memory usage:** Top keys limited to top 5 to avoid unbounded memory
- **Minimal impact:** Statistics collection should add <2% overhead
- **Write to stderr:** Avoid mixing with stdout log output

**Performance Targets:**
- Statistics overhead <2% of processing time
- Memory usage <10MB for stats (even with 1M+ lines)
- No blocking or slowdown during collection

## Deliverables

- [ ] Statistics collector class
- [ ] `--stats`, `--stats-only`, `--stats-json` flags
- [ ] Formatted text summary output
- [ ] JSON output option
- [ ] Integration into main processing loop
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Performance validation (overhead <2%)
- [ ] Documentation with examples
- [ ] Edge case handling

## Future Extensions (Not in Phase 5)

- Export stats to file (CSV, JSON)
- Real-time stats (update during processing)
- More detailed metrics (P50, P95, P99 latencies)
- Custom stat collectors (user-defined)
- Histogram of key distributions
- Timeline view (logs per minute/hour)

## Dependencies

- Python `collections.Counter` (stdlib)
- Python `time` (stdlib)
- Python `json` (stdlib) - for JSON output
- No new external dependencies

## Notes

This is a standalone feature that integrates cleanly with existing functionality. It provides valuable insights with minimal performance impact and no external dependencies.
