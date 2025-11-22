# Phase 3: Filtering (Stern-Aligned)

**Priority:** HIGH
**External Dependencies:** None (uses re from stdlib for regex)
**Estimated Complexity:** Medium

## Objectives

Implement filtering capabilities aligned with stern's behavior to reduce noise in high-volume logs. Focus on `--include`, `--exclude`, and `--field-selector` patterns that work naturally with JSON log streaming.

## Features

### Stern-Aligned Filtering

**Goal:** Filter log entries using patterns similar to stern for familiarity

**Inspiration:** stern (Kubernetes log tailer)

**Proposed Flags:**

```bash
# Include: Show only lines matching regex (allowlist)
tail-jsonl --include='error|warning'
tail-jsonl -i 'transaction'

# Exclude: Hide lines matching regex (blocklist)
tail-jsonl --exclude='DEBUG|TRACE'
tail-jsonl -e 'health_check'

# Field selector: Filter by extracted field values (supports dotted keys)
tail-jsonl --field-selector='level=error'
tail-jsonl --field-selector='log.level=debug'  # Dotted key
tail-jsonl --field-selector='host=prod-*'      # Glob pattern

# Combined filtering (AND logic)
tail-jsonl -i 'payment' -e 'test' --field-selector='level=error'
```

**Key Differences from Original Plan:**
- Replace generic `--filter` with stern's `--include`/`--exclude` pattern
- Use `--field-selector` instead of `--level` for more flexible field-based filtering
- Support regex for include/exclude (stern compatibility)
- Support glob patterns for field-selector values
- Apply filters to formatted output (what user sees) for simplicity

**Scope for Phase 3:**
- ✅ `--include` / `-i`: Regex allowlist filtering
- ✅ `--exclude` / `-e`: Regex blocklist filtering
- ✅ `--field-selector`: Filter by extracted field key=value with glob support
- ✅ Multiple field selectors (AND logic)
- ✅ Case-insensitive regex option
- ❌ JQ-style filtering (deferred to future phase)

**Implementation Plan:**

1. **Extend Config with filter fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       include_pattern: str | None = None      # Regex allowlist
       exclude_pattern: str | None = None      # Regex blocklist
       field_selectors: list[tuple[str, str]] | None = None  # [(key, value_pattern), ...]
       case_insensitive: bool = False          # For regex matching

       # Compiled patterns (cached)
       _include_re: re.Pattern | None = field(default=None, init=False, repr=False)
       _exclude_re: re.Pattern | None = field(default=None, init=False, repr=False)

   def __post_init__(self) -> None:
       """Compile regex patterns for performance."""
       flags = re.IGNORECASE if self.case_insensitive else 0
       if self.include_pattern:
           self._include_re = re.compile(self.include_pattern, flags)
       if self.exclude_pattern:
           self._exclude_re = re.compile(self.exclude_pattern, flags)
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       # ... existing params ...
       help={
           'include': 'Include only lines matching regex pattern (like stern -i)',
           'i': 'Alias for --include',
           'exclude': 'Exclude lines matching regex pattern (like stern -e)',
           'e': 'Alias for --exclude',
           'field-selector': 'Filter by field key=value (supports globs). Can be repeated. (like stern --field-selector)',
           'case-insensitive': 'Case-insensitive regex matching for include/exclude',
       }
   )
   def main(
       ctx,
       include=None,
       i=None,  # Alias for include
       exclude=None,
       e=None,  # Alias for exclude
       field_selector=None,
       case_insensitive=False,
       ...
   ):
       # Resolve aliases
       include_pattern = include or i
       exclude_pattern = exclude or e
   ```

3. **Implement filter logic:**
   ```python
   # tail_jsonl/_private/filters.py
   import re
   from fnmatch import fnmatch

   def should_include_record(
       record: Record,
       formatted_output: str,
       config: Config
   ) -> bool:
       """Return True if record passes all filters.

       Args:
           record: Parsed log record
           formatted_output: The formatted string that will be displayed
           config: Configuration with filter settings
       """
       # Field selectors (applied to extracted fields before formatting)
       if config.field_selectors:
           for key, pattern in config.field_selectors:
               # Try to get value from extracted fields
               # Support dotted keys (e.g., 'log.level')
               if '.' in key:
                   # Check if it's one of the standard extracted fields with dotted notation
                   value = None
                   # Check in record's standard fields first
                   if key in ['timestamp', 'level', 'message']:
                       value = getattr(record, key, None)
                   # Then check in data dict (might be a promoted dotted key)
                   if value is None:
                       value = record.data.get(key)
               else:
                   # Simple key lookup
                   # First check standard fields
                   if key == 'timestamp':
                       value = record.timestamp
                   elif key == 'level':
                       value = record.level
                   elif key == 'message':
                       value = record.message
                   else:
                       value = record.data.get(key)

               if value is None:
                   return False  # Key doesn't exist, exclude record

               # Match against pattern (glob)
               if not fnmatch(str(value).lower(), pattern.lower()):
                   return False

       # Include pattern (allowlist - applied to formatted output)
       if config._include_re:
           if not config._include_re.search(formatted_output):
               return False

       # Exclude pattern (blocklist - applied to formatted output)
       if config._exclude_re:
           if config._exclude_re.search(formatted_output):
               return False

       return True
   ```

4. **Integrate into print_record:**
   ```python
   def print_record(line: str, console: Console, config: Config) -> None:
       record = parse_record(line)
       if not record:
           return

       # Apply field selectors first (before formatting)
       if config.field_selectors:
           if not should_include_record_field_selectors(record, config):
               return

       # Format the record
       formatted = format_record(record, console, config)

       # Apply include/exclude patterns to formatted output
       if not should_include_formatted(formatted, config):
           return

       # Print the record
       console.print(formatted, markup=False, highlight=False)
   ```

5. **Handle edge cases:**
   - Invalid regex patterns (catch and report error)
   - Missing field selector keys in log
   - Case sensitivity for field selectors (normalize to lowercase)
   - Empty patterns
   - Regex compilation errors

**Acceptance Criteria:**
- [ ] `--include` / `-i` filters to lines matching regex
- [ ] `--exclude` / `-e` filters out lines matching regex
- [ ] `--field-selector` filters by field key=value with glob support
- [ ] Multiple field selectors work with AND logic
- [ ] Dotted keys work in field selectors (e.g., `log.level=debug`)
- [ ] Standard extracted fields work (timestamp, level, message)
- [ ] Case-insensitive option works for regex
- [ ] Invalid patterns handled gracefully with clear errors
- [ ] Comprehensive unit tests with parameterized cases
- [ ] Edge cases handled gracefully
- [ ] Performance tested with benchmarks
- [ ] Documentation updated with stern-style examples

### 4.11 Configuration Validation

**Goal:** Validate config file syntax and report errors clearly

**Proposed Flag:**
```bash
tail-jsonl --validate-config ~/.tail-jsonl.toml
```

**Implementation Plan:**

1. **Add validation function:**
   ```python
   def validate_config(config_path: Path) -> list[str]:
       """Validate config file and return list of errors."""
       errors = []
       try:
           config = Config.load_from_path(config_path)
       except toml.TOMLDecodeError as e:
           errors.append(f"TOML syntax error: {e}")
           return errors

       # Validate dotted keys
       for key in config.keys.on_own_line:
           if not key:
               errors.append("Empty key in keys.on_own_line")

       # Validate regex patterns
       if config.include_pattern:
           try:
               re.compile(config.include_pattern)
           except re.error as e:
               errors.append(f"Invalid include pattern: {e}")

       if config.exclude_pattern:
           try:
               re.compile(config.exclude_pattern)
           except re.error as e:
               errors.append(f"Invalid exclude pattern: {e}")

       return errors
   ```

2. **Add CLI flag:**
   ```python
   @invoke.task(
       help={'validate-config': 'Validate config file and exit'}
   )
   def main(ctx, validate_config=None, ...):
       if validate_config:
           errors = validate_config_file(Path(validate_config))
           if errors:
               console.print("[red]Config validation failed:[/red]")
               for error in errors:
                   console.print(f"  - {error}")
               sys.exit(1)
           console.print("[green]Config is valid[/green]")
           sys.exit(0)
   ```

**Acceptance Criteria:**
- [ ] `--validate-config` flag validates TOML syntax
- [ ] Validates regex patterns (include/exclude)
- [ ] Validates dotted keys configuration
- [ ] Clear error messages for validation failures
- [ ] Exit code 0 on success, 1 on failure
- [ ] Unit tests for validation logic
- [ ] Documentation with examples

## Testing Strategy

**Approach:** TDD with parameterized tests

1. **Include/Exclude regex tests:**
   ```python
   @pytest.mark.parametrize('output,include,exclude,expected', [
       ('ERROR: failed', 'error', None, True),       # Case insensitive by default
       ('DEBUG: trace', None, 'DEBUG|TRACE', False), # Exclude match
       ('INFO: ok', 'error', None, False),           # Include no match
       ('ERROR: test', 'error', 'test', False),      # Exclude takes precedence
   ])
   def test_include_exclude_filter(output, include, exclude, expected):
       # Test implementation
   ```

2. **Field selector tests:**
   ```python
   @pytest.mark.parametrize('record,selector,expected', [
       ({'level': 'error'}, ('level', 'error'), True),
       ({'level': 'info'}, ('level', 'error'), False),
       ({'host': 'prod-1'}, ('host', 'prod-*'), True),      # Glob
       ({'log': {'level': 'debug'}}, ('log.level', 'debug'), True),  # Dotted key
   ])
   def test_field_selector(record, selector, expected):
       # Test implementation
   ```

3. **Integration tests:**
   - Process stream with combined filters
   - Verify correct records pass through
   - Verify filtered records excluded
   - Test stern-like usage patterns

4. **Regex compilation tests:**
   - Valid patterns compile
   - Invalid patterns fail with clear errors
   - Case sensitivity works correctly

## Performance Considerations

- Pre-compile regex patterns at config initialization (O(1) per line)
- Use early returns to skip processing filtered records
- Field selector evaluation should be O(k) where k is number of selectors
- Regex matching overhead should be minimal for simple patterns
- Benchmark filtering overhead (<5% impact on throughput)

**Optimizations:**
- Cache compiled regex patterns
- Evaluate field selectors before formatting (cheaper)
- Evaluate regex patterns on formatted output (what user sees)

## Performance Targets

- Filtering adds <5% overhead to processing time
- Regex matching acceptable for typical patterns
- Memory usage unchanged (no buffering)

## Deliverables

- [ ] `--include` / `-i` regex allowlist implementation
- [ ] `--exclude` / `-e` regex blocklist implementation
- [ ] `--field-selector` with glob support
- [ ] Dotted key support in field selectors
- [ ] Case-insensitive option
- [ ] Config validation command
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Benchmarks showing filter performance
- [ ] Documentation with stern-style examples
- [ ] Updated README with filtering section

## Stern Compatibility Notes

**Similarities:**
- `-i` / `--include` for allowlist filtering
- `-e` / `--exclude` for blocklist filtering
- `--field-selector` for field-based filtering
- Regex support for include/exclude

**Differences:**
- stern's `--field-selector` is Kubernetes-specific (e.g., `spec.nodeName`)
- tail-jsonl's `--field-selector` works with extracted JSON fields
- tail-jsonl supports glob patterns in field selector values
- tail-jsonl applies filters to formatted output for simplicity

## Future Extensions (Not in Phase 3)

- OR logic for field selectors
- Inverse field selectors (e.g., `field!=value`)
- JQ-style filtering (needs jq dependency)
- Advanced regex features (lookahead, etc.)
