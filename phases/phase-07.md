# Phase 7: Context Lines

**Priority:** LOW
**External Dependencies:** None (uses stdlib with collections.deque)
**Estimated Complexity:** Medium-High

## Objectives

Implement context lines similar to `grep -A/-B/-C` to show N lines before and/or after search matches. This helps understand the context around important log events.

## Features

### 4.14 Context Lines

**Goal:** Show N lines before/after matching patterns

**Example Usage:**

```bash
# Show 3 lines after each error
tail-jsonl --search='error' -A 3

# Show 3 lines before each error
tail-jsonl --search='error' -B 3

# Show 3 lines before and after
tail-jsonl --search='error' -C 3

# Equivalent to -C 3
tail-jsonl --search='error' -A 3 -B 3
```

**Example Output:**

```
# Normal log lines
INFO | Starting service
INFO | Loading config
INFO | Connecting to database
ERROR | Connection failed: timeout
INFO | Retrying connection (attempt 1)
INFO | Retrying connection (attempt 2)
INFO | Connection successful
--
INFO | Processing request
DEBUG | Validating input
ERROR | Invalid user ID
WARNING | Using default value
INFO | Request completed
```

**Similar to:** `grep -A/-B/-C`

**Implementation Plan:**

1. **Add config fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       context_after: int = 0   # Lines after match (-A)
       context_before: int = 0  # Lines before match (-B)
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       help={
           'A': 'Show N lines after each match (like grep -A)',
           'B': 'Show N lines before each match (like grep -B)',
           'C': 'Show N lines before and after each match (like grep -C)',
       }
   )
   def main(ctx, A=0, B=0, C=0, ...):
       # C is shorthand for both A and B
       if C:
           A = B = C
   ```

3. **Implement context buffering:**
   ```python
   # tail_jsonl/_private/context.py
   from collections import deque
   from dataclasses import dataclass
   from typing import Deque, Optional

   @dataclass
   class ContextBuffer:
       """Buffer for managing context lines around matches."""
       before: int  # Number of lines to show before match
       after: int   # Number of lines to show after match

       # Internal state
       _before_buffer: Deque[str] = field(default_factory=deque)
       _after_counter: int = 0
       _last_match_line: Optional[int] = None
       _current_line: int = 0

       def __post_init__(self):
           # Initialize deque with maxlen for before buffer
           self._before_buffer = deque(maxlen=self.before)

       def add_line(self, line: str, is_match: bool) -> tuple[bool, list[str]]:
           """
           Add a line to the context buffer.

           Returns:
               (should_print, before_lines):
                   - should_print: True if this line should be printed
                   - before_lines: List of before-context lines to print (empty if none)
           """
           self._current_line += 1
           should_print = False
           before_lines = []

           # If we're in "after" mode from a previous match
           if self._after_counter > 0:
               should_print = True
               self._after_counter -= 1

           # If this line matches
           if is_match:
               # Print buffered before-context lines
               if self.before > 0 and self._before_buffer:
                   before_lines = list(self._before_buffer)
                   self._before_buffer.clear()

               should_print = True
               self._after_counter = self.after
               self._last_match_line = self._current_line

           # If not printing, add to before buffer
           elif not should_print and self.before > 0:
               self._before_buffer.append(line)

           return should_print, before_lines

       def should_print_separator(self) -> bool:
           """Return True if we should print a separator (--) between context groups."""
           # Print separator if we've printed all after-context and are skipping lines
           return (
               self._after_counter == 0
               and self._last_match_line is not None
               and self._current_line > self._last_match_line + self.after
           )
   ```

4. **Integrate into main processing:**
   ```python
   def process_logs_with_context(console: Console, config: Config):
       """Process logs with context line support."""
       context = None
       if config.context_before > 0 or config.context_after > 0:
           context = ContextBuffer(
               before=config.context_before,
               after=config.context_after,
           )

       need_separator = False

       with fileinput.input() as _f:
           for line in _f:
               record = parse_record(line)
               if not record:
                   continue

               # Determine if this line matches search
               is_match = matches_search(record, config) if config.search_pattern else True

               if context:
                   should_print, before_lines = context.add_line(line, is_match)

                   # Print separator if needed
                   if need_separator and context.should_print_separator():
                       console.print("--")
                       need_separator = False

                   # Print before-context lines
                   for before_line in before_lines:
                       before_record = parse_record(before_line)
                       if before_record:
                           print_record_formatted(before_record, console, config)

                   # Print current line if should print
                   if should_print:
                       print_record_formatted(record, console, config)
                       need_separator = True
               else:
                   # No context, normal filtering
                   if is_match:
                       print_record_formatted(record, console, config)
   ```

5. **Handle edge cases:**
   - Context lines at start of stream (before buffer not full)
   - Context lines at end of stream
   - Overlapping context regions (match within N lines of previous match)
   - Separator placement between context groups
   - Context with filters (show context even if filtered?)
   - Memory usage with large before buffer

**Acceptance Criteria:**
- [ ] `-A N` shows N lines after matches
- [ ] `-B N` shows N lines before matches
- [ ] `-C N` shows N lines before and after matches
- [ ] Separator `--` between non-contiguous context groups
- [ ] Before buffer limited to N lines (memory efficient)
- [ ] Overlapping context handled correctly (no duplicates)
- [ ] Works with search/filter flags
- [ ] Edge cases handled (start/end of stream)
- [ ] Comprehensive unit tests
- [ ] Performance acceptable (minimal overhead)
- [ ] Documentation with examples

## Testing Strategy

**Approach:** TDD with synthetic log sequences

1. **Context buffer unit tests:**
   ```python
   def test_context_after():
       buffer = ContextBuffer(before=0, after=2)

       # Line 1: no match
       should_print, before = buffer.add_line("line1", is_match=False)
       assert not should_print
       assert before == []

       # Line 2: match
       should_print, before = buffer.add_line("line2", is_match=True)
       assert should_print
       assert before == []

       # Lines 3-4: after context
       should_print, _ = buffer.add_line("line3", is_match=False)
       assert should_print

       should_print, _ = buffer.add_line("line4", is_match=False)
       assert should_print

       # Line 5: no longer in context
       should_print, _ = buffer.add_line("line5", is_match=False)
       assert not should_print
   ```

2. **Context before tests:**
   ```python
   def test_context_before():
       buffer = ContextBuffer(before=2, after=0)

       # Lines 1-2: no match (go into buffer)
       buffer.add_line("line1", is_match=False)
       buffer.add_line("line2", is_match=False)

       # Line 3: match (should flush buffer)
       should_print, before = buffer.add_line("line3", is_match=True)
       assert should_print
       assert before == ["line1", "line2"]
   ```

3. **Overlapping context tests:**
   ```python
   def test_overlapping_context():
       # Test matches within N lines of each other
       # Ensure no duplicate lines printed
   ```

4. **Integration tests:**
   - Process real logs with -A/-B/-C
   - Verify correct lines printed
   - Verify separator placement
   - Check memory usage with large buffers

5. **Edge case tests:**
   - Match on first line (no before context available)
   - Match on last line (truncated after context)
   - All lines match (continuous context)
   - No lines match (no output)
   - Before buffer larger than input

## Performance Considerations

- **Memory usage:** Before buffer limited by deque maxlen
- **CPU overhead:** Minimal - simple counter logic
- **Buffering impact:** Must buffer before-context, could impact streaming
- **Large buffers:** -B 1000 could use significant memory

**Optimizations:**
- Use `collections.deque` with maxlen for efficient before buffer
- Early exit logic to avoid unnecessary processing
- Reuse parsed records instead of re-parsing

**Performance Targets:**
- Context overhead <5% for typical usage (-A/-B 3)
- Memory usage: O(B) where B is before buffer size
- No impact when context not used
- Handle 10K+ lines/sec with context enabled

## Deliverables

- [ ] ContextBuffer class implementation
- [ ] `-A`, `-B`, `-C` CLI flags
- [ ] Integration into main processing loop
- [ ] Separator logic between context groups
- [ ] Overlapping context handling
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Performance benchmarks
- [ ] Memory usage validation
- [ ] Documentation with examples
- [ ] Edge case handling

## Future Extensions (Not in Phase 7)

- Colored context lines (dim vs bright for matches)
- Line numbers (like grep -n)
- Group context by time window instead of line count
- Context in statistics (count context lines separately)

## Dependencies

- Python `collections.deque` (stdlib)
- No external dependencies

## Notes

Context lines add significant value for debugging but require careful buffering logic. The implementation must handle edge cases like overlapping contexts and manage memory efficiently.

Consider interaction with other features:
- Context + filtering: Show context even if filtered?
- Context + stats: Count context lines in stats?
- Context + highlighting: Apply highlighting to context lines?

Default behavior should match grep's behavior where possible for familiarity.
