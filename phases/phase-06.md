# Phase 6: Timestamp Formatting ⚠️ REVIEW REQUIRED

**Priority:** LOW-MEDIUM
**External Dependencies:** Optional `arrow` or `python-dateutil` for parsing, optional `humanize` for relative times
**Estimated Complexity:** Medium
**Status:** 🔍 **REVIEWED**

## ⚠️ Review Questions

Before implementing this phase, please review and decide:

1. **Dependency choice for timestamp parsing:**
   - **Option A:** Use stdlib `datetime.fromisoformat()` (Python 3.7+)
     - ✅ No dependencies
     - ❌ Limited format support (ISO 8601 only)
     - ❌ No timezone handling for complex formats

   - **Option B:** Use `python-dateutil` for flexible parsing
     - ✅ Handles many formats automatically
     - ✅ Good timezone support
     - ❌ Adds dependency

   - [x] **Option C:** Use `arrow` for parsing and formatting
     - ✅ Modern API, good format support
     - ✅ Built-in humanize for relative times
     - ❌ Adds dependency

2. **Relative time formatting:**
   - **Option A:** Implement basic relative time in stdlib
     - ✅ No dependency
     - ❌ Basic functionality only

   - **Option B:** Use `humanize` library
     - ✅ Rich formatting ("2 hours ago", "just now")
     - ❌ Adds dependency

   - [x] **Option C:** Use `arrow.humanize()`
     - ✅ Good formatting
     - ❌ Requires arrow dependency

3. **Timestamp field detection:**
   - Hardcode common field names (timestamp, @timestamp, time, ts)?
   - [x] Allow user to configure field name? (extend the existing logic to provide different variations of dot syntax to look for)
   - Auto-detect by looking for ISO 8601 format?

4. **Timezone handling:**
   - Always display in UTC?
   - Convert to local timezone?
   - [x] Allow user to specify timezone? (provide a CLI argument that will convert to the specified timezone where no value means to use computer TZ. Default to unmodified or UTC)

5. **Performance:**
   - Is timestamp parsing overhead acceptable?
   - Should we cache parsed timestamps?
   - [x] Make timestamp formatting optional (opt-in)? (CLI argument to select one of a subset of formats supported by arrow)

**Recommended Approach (Subject to Review):**
- Start with stdlib only (no dependencies)
- Support ISO 8601 format only (most common in JSON logs)
- Add basic relative time without humanize
- Make it easy to add dependencies later if needed

## Objectives

Provide flexible timestamp formatting to improve log readability. Balance functionality with minimal dependencies and acceptable performance overhead.

## Features

### 4.9 Timestamp Formatting

**Goal:** Customize timestamp display for better readability

**Example Usage:**

```bash
# Default: show full ISO 8601 timestamp
tail-jsonl
# 2024-01-15T14:23:45.123456Z | INFO | message

# Custom strftime format
tail-jsonl --time-format='%H:%M:%S'
# 14:23:45 | INFO | message

# Relative times
tail-jsonl --time-format='relative'
# 2s ago | INFO | message
# 5m ago | WARNING | another message

# Hide timestamps
tail-jsonl --no-time
# INFO | message

# Specify timestamp field (if not 'timestamp')
tail-jsonl --time-field='@timestamp'
```

**Implementation Plan (stdlib-only approach):**

1. **Add config fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       time_format: str | None = None  # strftime format or 'relative'
       time_field: str = 'timestamp'  # Field name to use
       show_time: bool = True  # False for --no-time
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       help={
           'time-format': 'Timestamp format: strftime pattern or "relative" (default: ISO 8601)',
           'time-field': 'Name of timestamp field (default: timestamp)',
           'no-time': 'Hide timestamps from output',
       }
   )
   def main(ctx, time_format=None, time_field='timestamp', no_time=False, ...):
   ```

3. **Implement timestamp parsing (stdlib only):**
   ```python
   # tail_jsonl/_private/timestamp.py
   from datetime import datetime
   from typing import Optional

   def parse_timestamp(value: str | int | float) -> Optional[datetime]:
       """Parse timestamp from various formats using stdlib only."""
       if isinstance(value, (int, float)):
           # Assume Unix epoch
           try:
               return datetime.fromtimestamp(value)
           except (ValueError, OSError):
               return None

       if isinstance(value, str):
           # Try ISO 8601 format
           try:
               # Handle both with and without timezone
               if value.endswith('Z'):
                   value = value[:-1] + '+00:00'
               return datetime.fromisoformat(value)
           except ValueError:
               return None

       return None

   def format_timestamp(dt: datetime, format_str: str) -> str:
       """Format timestamp according to config."""
       if format_str == 'relative':
           return format_relative(dt)
       else:
           # strftime format
           return dt.strftime(format_str)

   def format_relative(dt: datetime) -> str:
       """Format as relative time using stdlib only."""
       now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
       delta = now - dt

       # Future timestamps
       if delta.total_seconds() < 0:
           delta = -delta
           suffix = 'from now'
       else:
           suffix = 'ago'

       seconds = delta.total_seconds()

       if seconds < 60:
           return f"{int(seconds)}s {suffix}"
       elif seconds < 3600:
           return f"{int(seconds / 60)}m {suffix}"
       elif seconds < 86400:
           return f"{int(seconds / 3600)}h {suffix}"
       else:
           return f"{int(seconds / 86400)}d {suffix}"
   ```

4. **Integrate into formatting:**
   ```python
   def format_record(record: Record, config: Config) -> str:
       """Format record with optional timestamp formatting."""
       # Extract timestamp
       timestamp_str = None
       if config.show_time and config.time_field in record.data:
           raw_timestamp = record.data[config.time_field]
           dt = parse_timestamp(raw_timestamp)

           if dt:
               if config.time_format:
                   timestamp_str = format_timestamp(dt, config.time_format)
               else:
                   # Default: ISO 8601
                   timestamp_str = dt.isoformat()

       # Build output with formatted timestamp
       if timestamp_str:
           parts = [timestamp_str]
       else:
           parts = []

       # ... rest of formatting ...
   ```

5. **Handle edge cases:**
   - Invalid timestamp values
   - Missing timestamp field
   - Unparseable formats (with stdlib limitation)
   - Timezone-naive vs timezone-aware datetimes
   - Future timestamps (relative time)
   - Very old/new timestamps (epoch edge cases)

**Implementation Plan (with optional dependencies):**

If review approves adding dependencies:

1. **Add optional dependencies:**
   ```toml
   [tool.poetry.dependencies]
   # ... existing ...

   [tool.poetry.group.time]
   optional = true

   [tool.poetry.group.time.dependencies]
   arrow = "^1.3.0"  # For flexible parsing and humanize

   [tool.poetry.extras]
   time = ["arrow"]
   ```

2. **Use arrow for better functionality:**
   ```python
   def parse_timestamp_arrow(value) -> Optional[arrow.Arrow]:
       """Parse timestamp using arrow for better format support."""
       try:
           if isinstance(value, (int, float)):
               return arrow.get(value)
           else:
               return arrow.get(value)
       except arrow.parser.ParserError:
           return None

   def format_relative_arrow(dt: arrow.Arrow) -> str:
       """Format using arrow's humanize."""
       return dt.humanize()
   ```

**Acceptance Criteria:**
- [ ] Review decisions documented and approved
- [ ] Timestamp parsing from common formats
- [ ] Custom strftime format support
- [ ] Relative time formatting
- [ ] `--no-time` flag to hide timestamps
- [ ] Configurable timestamp field name
- [ ] Handle missing/invalid timestamps gracefully
- [ ] Performance overhead <5%
- [ ] Comprehensive unit tests
- [ ] Documentation with examples

## Testing Strategy

**Approach:** TDD with various timestamp formats

1. **Parsing tests:**
   ```python
   @pytest.mark.parametrize('value,expected_timestamp', [
       ('2024-01-15T14:23:45Z', datetime(2024, 1, 15, 14, 23, 45)),
       ('2024-01-15T14:23:45.123456+00:00', datetime(2024, 1, 15, 14, 23, 45, 123456)),
       (1705329825, datetime(2024, 1, 15, 14, 23, 45)),  # Unix epoch
       ('invalid', None),
   ])
   def test_timestamp_parsing(value, expected_timestamp):
       result = parse_timestamp(value)
       if expected_timestamp:
           assert result.replace(tzinfo=None) == expected_timestamp
       else:
           assert result is None
   ```

2. **Formatting tests:**
   ```python
   @pytest.mark.parametrize('dt,format_str,expected', [
       (datetime(2024, 1, 15, 14, 23, 45), '%H:%M:%S', '14:23:45'),
       (datetime(2024, 1, 15, 14, 23, 45), '%Y-%m-%d', '2024-01-15'),
   ])
   def test_timestamp_formatting(dt, format_str, expected):
       assert format_timestamp(dt, format_str) == expected
   ```

3. **Relative time tests:**
   ```python
   def test_relative_time():
       now = datetime.now()
       past = now - timedelta(seconds=30)
       assert format_relative(past) == '30s ago'

       past = now - timedelta(minutes=5)
       assert format_relative(past) == '5m ago'
   ```

4. **Integration tests:**
   - Process logs with various timestamp formats
   - Verify formatting applied correctly
   - Test with missing timestamps
   - Performance tests with timestamp parsing

## Performance Considerations

- **Parsing overhead:** Each timestamp parse adds CPU time
- **Caching:** Consider caching if same timestamp appears multiple times (unlikely in logs)
- **Format complexity:** strftime is fast, relative time requires delta calculation
- **Make it optional:** Only parse if time-format specified

**Performance Targets:**
- Timestamp formatting overhead <5%
- No impact if --no-time used
- Handle 10K+ lines/sec with timestamp formatting

## Deliverables

- [ ] Review decisions and dependency choices approved
- [ ] Timestamp parsing implementation
- [ ] strftime format support
- [ ] Relative time formatting
- [ ] `--no-time`, `--time-format`, `--time-field` flags
- [ ] Graceful handling of missing/invalid timestamps
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Performance benchmarks
- [ ] Documentation with examples
- [ ] Optional dependency setup (if approved)

## Future Extensions (Not in Phase 6)

- Auto-detect timestamp field name
- Support multiple timestamp formats in single stream
- Convert between timezones
- Millisecond precision display
- Custom date/time separators

## Dependencies

**Minimal (stdlib-only) approach:**
- Python `datetime` (stdlib)
- Python `time` (stdlib)
- No external dependencies

**Enhanced (optional) approach:**
- `arrow` or `python-dateutil` for parsing
- `humanize` or `arrow.humanize()` for relative times
- Add as optional extras: `pip install tail-jsonl[time]`

## Notes

⚠️ **STOP: Do not implement until review questions are answered.**

Key decision: stdlib-only vs. optional dependencies. Stdlib approach keeps tool lean but limits functionality. Optional dependencies provide better UX but add complexity.

Recommendation: Start with stdlib, add optional extras if users request richer functionality.
