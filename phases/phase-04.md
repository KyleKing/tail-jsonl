# Phase 4: Search & Highlighting ⚠️ REVIEW REQUIRED

**Priority:** MEDIUM
**External Dependencies:** None (uses Rich's built-in highlighting)
**Estimated Complexity:** Medium
**Status:** 🔍 **REVIEWED**

## ⚠️ Review Questions

Before implementing this phase, please review and decide:

1. **Search scope:** Should search apply to:
   - [x] Only formatted output (what user sees)?
   - Raw JSON values?
   - Both?

2. **Highlighting behavior:**
   - [x] Highlight all occurrences in output?
   - Only highlight in specific fields (e.g., message)?
   - Different colors for different match types?

3. **Filter vs Highlight:**
   - `--search` shows only matching lines (like grep)?
   - [x] `--highlight` highlights matches but shows all lines?
   - Or combined flag with behavior option?

4. **Regex complexity:**
   - Basic string search only?
   - Full regex support?
   - [x] Limit regex features for safety/performance?

5. **Case sensitivity:**
   - Default case-insensitive or case-sensitive?
   - [x] Flag to toggle (e.g., `-i` like grep)?

6. **Performance concerns:**
   - [x] Acceptable overhead for regex matching?
   - Should we cache compiled patterns?
   - Limit to certain log volume?

## Objectives

Implement search and highlighting to help users quickly identify relevant information in logs. This feature should integrate seamlessly with existing filtering (Phase 3) and maintain the tool's performance characteristics.

## Features

### 4.3 Search & Highlighting

**Goal:** Search for patterns and highlight matches in log output

**Proposed Flags (Subject to Review):**

```bash
# Basic search (show only matching lines)
tail-jsonl --search='error'

# Highlight matches (show all lines, highlight matches)
tail-jsonl --highlight='user_id'

# Regex search
tail-jsonl --search='user_id:\d+' --regex

# Case-insensitive search (like grep -i)
tail-jsonl --search='ERROR' -i

# Combined with filtering
tail-jsonl --level=error --search='database' --highlight
```

**Implementation Options:**

**Option A: Simple String Search**
- Fastest implementation
- Uses Python `str.find()` or `in` operator
- No regex engine overhead
- Limited flexibility

**Option B: Rich's highlight_regex()**
- Built-in to Rich library
- Good performance for simple patterns
- Automatic color highlighting
- Regex support included

**Option C: Full Regex with re module**
- Maximum flexibility
- Pre-compile patterns for performance
- More complex implementation
- Potential security concerns with user patterns

**Recommended Approach (Subject to Review):**
Start with Option B (Rich's highlight_regex) for good balance of features and performance.

**Implementation Plan (Draft):**

1. **Add search config:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       search_pattern: str | None = None
       search_regex: bool = False
       search_case_sensitive: bool = False
       search_filter_only: bool = False  # True = filter, False = highlight
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       help={
           'search': 'Search pattern to find (filters to matching lines)',
           'highlight': 'Pattern to highlight (shows all lines)',
           'regex': 'Treat search/highlight pattern as regex',
           'i': 'Case-insensitive search',
       }
   )
   def main(ctx, search=None, highlight=None, regex=False, i=False, ...):
   ```

3. **Implement search logic:**
   ```python
   def matches_search(record: Record, config: Config) -> bool:
       """Return True if record matches search pattern."""
       if not config.search_pattern:
           return True

       search_text = get_searchable_text(record)  # Decision needed: what to search?

       if config.search_regex:
           import re
           flags = re.IGNORECASE if not config.search_case_sensitive else 0
           pattern = re.compile(config.search_pattern, flags)
           return pattern.search(search_text) is not None
       else:
           if not config.search_case_sensitive:
               return config.search_pattern.lower() in search_text.lower()
           return config.search_pattern in search_text
   ```

4. **Implement highlighting:**
   ```python
   def apply_highlighting(text: str, config: Config) -> Text:
       """Apply highlighting to text using Rich."""
       if not config.highlight_pattern:
           return Text(text)

       from rich.highlighter import RegexHighlighter

       class PatternHighlighter(RegexHighlighter):
           highlights = [config.highlight_pattern]

       highlighter = PatternHighlighter()
       return highlighter(text)
   ```

5. **Integrate into print_record:**
   ```python
   def print_record(line: str, console: Console, config: Config) -> None:
       record = parse_record(line)

       # Filtering (Phase 3)
       if not should_include_record(record, config):
           return

       # Search filtering (Phase 4)
       if config.search_filter_only and not matches_search(record, config):
           return

       # Format record
       formatted = format_record(record, config)

       # Apply highlighting (Phase 4)
       if config.highlight_pattern:
           formatted = apply_highlighting(formatted, config)

       console.print(formatted)
   ```

**Edge Cases to Handle:**
- Invalid regex patterns (catch and error gracefully)
- Empty search patterns
- Search pattern not found (no output vs warning?)
- Performance with complex regex on high-volume logs
- Highlighting overlapping matches
- Special regex characters in non-regex mode

**Acceptance Criteria:**
- [ ] Review decisions documented and approved
- [ ] `--search` filters to matching lines
- [ ] `--highlight` highlights matches in all lines
- [ ] Regex support works correctly
- [ ] Case-insensitive mode works
- [ ] Invalid patterns handled gracefully
- [ ] Performance acceptable (benchmark against Phase 2 baseline)
- [ ] Integration tests with real log samples
- [ ] Documentation with examples
- [ ] Edge cases handled

## Testing Strategy

**Approach:** TDD with real-world log samples

1. **Search matching tests:**
   ```python
   @pytest.mark.parametrize('log,pattern,case_sensitive,should_match', [
       ('{"message": "ERROR: failed"}', 'error', False, True),
       ('{"message": "ERROR: failed"}', 'error', True, False),
       ('{"message": "user_id:123"}', r'user_id:\d+', False, True),
   ])
   def test_search_matching(log, pattern, case_sensitive, should_match):
       # Test implementation
   ```

2. **Highlighting tests:**
   - Verify Rich highlighting applied
   - Check correct spans highlighted
   - Validate color codes in output

3. **Integration tests:**
   - Search + filter combination
   - Highlight + search combination
   - Performance with large log streams

4. **Error handling tests:**
   - Invalid regex patterns
   - Empty patterns
   - Edge case patterns (e.g., `.*`, `^$`)

## Performance Considerations

- **Regex compilation:** Compile patterns once at startup
- **Search overhead:** Should be <10% impact on throughput
- **Highlighting overhead:** Rich's highlighter is optimized
- **Memory:** No buffering needed for search-only mode

**Performance Targets:**
- Search adds <10% overhead vs unfiltered processing
- Highlighting adds <15% overhead
- Handle 10K+ line streams without degradation

## Deliverables

- [ ] Review decisions documented and approved
- [ ] Search implementation (filter mode)
- [ ] Highlight implementation
- [ ] Regex support
- [ ] Case-insensitive mode
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Performance benchmarks
- [ ] Error handling for invalid patterns
- [ ] Documentation with examples
- [ ] Integration with Phase 3 filtering

## Future Extensions (Not in Phase 4)

- Multiple search patterns (OR logic)
- Named capture groups in regex
- Different highlight colors for different patterns
- Search history (if interactive mode added)
- Fuzzy search (requires external dependency)

## Dependencies

- Rich library (already a dependency) - for highlighting
- Python `re` module (stdlib) - for regex
- No new external dependencies

## Notes

⚠️ **STOP: Do not implement until review questions are answered.**

This phase requires UX decisions about search scope, behavior, and performance trade-offs. Once decisions are made, implementation is straightforward using Rich's built-in capabilities.
