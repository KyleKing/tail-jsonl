# Phase 4: Highlighting (Stern-Aligned) ✅ REVIEWED

**Priority:** MEDIUM
**External Dependencies:** None (uses Rich's built-in highlighting)
**Estimated Complexity:** Low-Medium
**Status:** 🔍 **REVIEWED**

## Review Decisions

1. **Search scope:** ✅ Only formatted output (what user sees)
2. **Highlighting behavior:** ✅ Highlight all occurrences in output
3. **Filter vs Highlight:** ✅ `--highlight` highlights matches but shows all lines (stern behavior)
4. **Regex complexity:** ✅ Full regex support with safety (compiled patterns)
5. **Case sensitivity:** ✅ Case-insensitive by default, flag to toggle
6. **Performance concerns:** ✅ Pre-compile and cache patterns

## Objectives

Implement highlighting aligned with stern's `--highlight` flag to visually emphasize matching patterns in log output. Unlike filtering (Phase 3), highlighting shows ALL lines but emphasizes matches for quick visual scanning.

## Features

### Stern-Aligned Highlighting

**Goal:** Highlight patterns in log output using stern's `--highlight` flag behavior

**Inspiration:** stern's `-H` / `--highlight` flag

**Proposed Flags:**

```bash
# Highlight pattern (shows all lines, highlights matches)
tail-jsonl --highlight='error|warning'
tail-jsonl -H 'exception'

# Case-sensitive highlighting
tail-jsonl --highlight='ERROR' --highlight-case-sensitive

# Multiple highlight patterns (different colors)
tail-jsonl -H 'error' -H 'warning' -H 'info'

# Combined with filtering (Phase 3)
tail-jsonl -i 'payment' -H 'error'  # Include payments, highlight errors
```

**Key Differences from Original Plan:**
- Simplified to match stern's behavior: highlight only, no filtering
- Filtering moved to Phase 3 (`--include`/`--exclude`)
- Focus on visual emphasis, not content filtering
- Apply highlighting to formatted output

**Scope for Phase 4:**
- ✅ `--highlight` / `-H`: Regex pattern highlighting
- ✅ Multiple highlight patterns with different colors
- ✅ Case-sensitive/insensitive toggle
- ✅ Integration with Rich's highlighting
- ❌ Interactive search (not useful for tailing)
- ❌ Context lines (moved to Phase 7)

**Implementation Plan:**

1. **Extend Config with highlight fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       highlight_patterns: list[str] | None = None  # List of regex patterns
       highlight_case_sensitive: bool = False

       # Compiled patterns (cached)
       _highlight_res: list[re.Pattern] | None = field(default=None, init=False, repr=False)

   def __post_init__(self) -> None:
       """Compile highlight patterns for performance."""
       if self.highlight_patterns:
           flags = 0 if self.highlight_case_sensitive else re.IGNORECASE
           self._highlight_res = [
               re.compile(pattern, flags)
               for pattern in self.highlight_patterns
           ]
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       # ... existing params ...
       help={
           'highlight': 'Highlight regex pattern in output (like stern -H). Can be repeated for multiple patterns.',
           'H': 'Alias for --highlight',
           'highlight-case-sensitive': 'Case-sensitive highlighting (default: case-insensitive)',
       }
   )
   def main(
       ctx,
       highlight=None,  # Can be list if repeated
       H=None,  # Alias for highlight
       highlight_case_sensitive=False,
       ...
   ):
       # Resolve aliases and combine patterns
       highlight_patterns = []
       if highlight:
           if isinstance(highlight, list):
               highlight_patterns.extend(highlight)
           else:
               highlight_patterns.append(highlight)
       if H:
           if isinstance(H, list):
               highlight_patterns.extend(H)
           else:
               highlight_patterns.append(H)
   ```

3. **Implement highlighting logic:**
   ```python
   # tail_jsonl/_private/highlighter.py
   import re
   from rich.text import Text
   from rich.style import Style

   # Color palette for multiple highlight patterns
   HIGHLIGHT_COLORS = [
       'yellow',
       'cyan',
       'magenta',
       'green',
       'blue',
       'red',
   ]

   def apply_highlighting(
       text: str,
       config: Config
   ) -> Text | str:
       """Apply regex highlighting to text using Rich.

       Args:
           text: Formatted output string
           config: Configuration with highlight patterns

       Returns:
           Rich Text object with highlighting, or original string if no highlights
       """
       if not config._highlight_res:
           return text

       # Create Rich Text object
       rich_text = Text(text)

       # Apply each highlight pattern with different color
       for i, pattern in enumerate(config._highlight_res):
           color = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
           style = Style(bgcolor=color, color='black', bold=True)

           # Find all matches
           for match in pattern.finditer(text):
               start, end = match.span()
               # Apply style to matched region
               rich_text.stylize(style, start, end)

       return rich_text
   ```

4. **Integrate into print_record:**
   ```python
   def print_record(line: str, console: Console, config: Config) -> None:
       record = parse_record(line)
       if not record:
           return

       # Apply filtering (Phase 3)
       if not should_include_record(record, formatted, config):
           return

       # Format the record
       formatted = format_record(record, console, config)

       # Apply highlighting (Phase 4)
       if config._highlight_res:
           formatted = apply_highlighting(formatted, config)

       # Print the record
       if isinstance(formatted, Text):
           console.print(formatted)  # Rich Text with highlighting
       else:
           console.print(formatted, markup=False, highlight=False)  # Plain string
   ```

5. **Handle edge cases:**
   - Invalid regex patterns (catch and report error)
   - Empty patterns
   - Overlapping matches (Rich handles this)
   - No matches (just show original text)
   - Too many patterns (cycle through colors)

**Acceptance Criteria:**
- [ ] `--highlight` / `-H` highlights regex patterns
- [ ] Multiple patterns use different colors
- [ ] Case-insensitive highlighting by default
- [ ] `--highlight-case-sensitive` works
- [ ] Invalid patterns handled gracefully
- [ ] Works with filtering flags (Phase 3)
- [ ] No performance degradation for unhighlighted output
- [ ] Overlapping matches handled correctly
- [ ] Comprehensive unit tests
- [ ] Documentation with stern-style examples

## Testing Strategy

**Approach:** TDD with parameterized tests

1. **Basic highlighting tests:**
   ```python
   @pytest.mark.parametrize('text,pattern,expected_highlights', [
       ('ERROR: failed', 'error', [(0, 5)]),  # Case insensitive
       ('ERROR and error', 'error', [(0, 5), (10, 15)]),  # Multiple matches
       ('no match', 'error', []),  # No highlights
   ])
   def test_highlight_regex(text, pattern, expected_highlights):
       # Test implementation
       # Verify Rich Text object has correct styling
   ```

2. **Multiple pattern tests:**
   ```python
   def test_multiple_highlight_patterns():
       patterns = ['error', 'warning', 'info']
       # Each pattern should get different color
       # Verify colors cycle correctly
   ```

3. **Case sensitivity tests:**
   ```python
   @pytest.mark.parametrize('text,pattern,case_sensitive,matches', [
       ('ERROR', 'error', False, True),
       ('ERROR', 'error', True, False),
   ])
   def test_highlight_case_sensitivity(text, pattern, case_sensitive, matches):
       # Test implementation
   ```

4. **Integration tests:**
   - Highlight with filtering
   - Multiple patterns with different colors
   - Edge cases (overlapping matches, no matches)

5. **Rich Text tests:**
   - Verify Text object created correctly
   - Verify styles applied to correct spans
   - Verify colors assigned correctly

## Performance Considerations

- Pre-compile regex patterns at config initialization
- Highlighting overhead only when patterns are specified
- Use Rich's optimized Text styling
- No impact on non-highlighted output

**Optimizations:**
- Cache compiled patterns
- Skip highlighting if no patterns
- Use Rich's built-in highlighting efficiently

## Performance Targets

- Highlighting adds <10% overhead (only when patterns specified)
- No overhead when no highlighting
- Handle multiple patterns efficiently

## Deliverables

- [ ] `--highlight` / `-H` regex highlighting implementation
- [ ] Multiple pattern support with color cycling
- [ ] Case-sensitive option
- [ ] Integration with Rich Text
- [ ] Regex compilation and caching
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Performance benchmarks
- [ ] Documentation with stern-style examples
- [ ] Updated README with highlighting section

## Stern Compatibility Notes

**Similarities:**
- `-H` / `--highlight` for pattern highlighting
- Regex support for highlight patterns
- Shows all lines (no filtering)

**Differences:**
- stern likely uses terminal escape codes
- tail-jsonl uses Rich for better color management
- tail-jsonl supports multiple patterns with different colors
- tail-jsonl has case-sensitivity toggle

## Future Extensions (Not in Phase 4)

- Custom highlight colors (user-configurable)
- Named patterns (e.g., `--highlight-error`, `--highlight-warning`)
- Highlight styles (underline, bold, italic, etc.)
- Different highlight modes (background, foreground, both)

## Dependencies

- Rich library (already a dependency) - for Text styling
- Python `re` module (stdlib) - for regex
- No new external dependencies

## Notes

This phase is now focused purely on highlighting, with all filtering moved to Phase 3. This aligns better with stern's behavior where `--highlight` and `--include`/`--exclude` are separate concerns.

The implementation is simpler and more modular:
- Phase 3: Filter what to show
- Phase 4: Highlight what's important
- Both work together seamlessly
