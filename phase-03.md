# Phase 3: Basic Filtering

**Priority:** HIGH
**External Dependencies:** None (uses fnmatch from stdlib)
**Estimated Complexity:** Medium

## Objectives

Implement core filtering capabilities to reduce noise in high-volume logs. Focus on the most common use cases: level filtering and key-value matching with glob patterns.

## Features

### 4.2 Filtering Capabilities (Core Subset)

**Goal:** Filter log entries before formatting to improve signal-to-noise ratio

**Inspiration:** angle-grinder, lnav, stern

**Proposed Flags:**

```bash
# Level filtering (common case)
tail-jsonl --level=error,warning
tail-jsonl --level=error

# Key-value glob matching
tail-jsonl --filter='host=prod-*'
tail-jsonl --filter='namespace=kube-system'

# Multiple filters (AND logic)
tail-jsonl --level=error --filter='host=prod-*'
```

**Scope for Phase 3:**
- ✅ Level filtering by exact match or list
- ✅ Key-value glob pattern matching
- ✅ Multiple filters (AND logic)
- ❌ JQ-style filtering (deferred to future phase - requires jq dependency)
- ❌ Regex filtering (deferred to Phase 4 with search)

**Implementation Plan:**

1. **Extend Config with filter fields:**
   ```python
   @dataclass
   class Config:
       # ... existing fields ...
       filter_levels: list[str] | None = None  # e.g., ['error', 'warning']
       filter_key_values: list[tuple[str, str]] | None = None  # e.g., [('host', 'prod-*')]
   ```

2. **Add CLI flags:**
   ```python
   @invoke.task(
       # ... existing params ...
       help={
           'level': 'Filter by log level(s), comma-separated (e.g., error,warning)',
           'filter': 'Filter by key=value pattern, supports globs (e.g., host=prod-*). Can be specified multiple times.',
       }
   )
   def main(
       ctx,
       # ... existing params ...
       level=None,
       filter=None,
   ):
   ```

3. **Implement filter predicates:**
   ```python
   # tail_jsonl/_private/filters.py
   from fnmatch import fnmatch

   def should_include_record(record: Record, config: Config) -> bool:
       """Return True if record passes all filters."""
       # Level filter
       if config.filter_levels and record.level:
           if record.level.lower() not in [l.lower() for l in config.filter_levels]:
               return False

       # Key-value filters (AND logic)
       if config.filter_key_values:
           for key, pattern in config.filter_key_values:
               value = record.data.get(key)
               if value is None:
                   return False  # Key doesn't exist
               if not fnmatch(str(value), pattern):
                   return False  # Value doesn't match pattern

       return True
   ```

4. **Integrate into print_record:**
   ```python
   def print_record(line: str, console: Console, config: Config) -> None:
       record = parse_record(line)
       if not should_include_record(record, config):
           return  # Skip filtered records
       # ... rest of processing ...
   ```

5. **Handle edge cases:**
   - Missing level field in log
   - Missing filter key in log
   - Case sensitivity (normalize to lowercase)
   - Empty filter lists

**Acceptance Criteria:**
- [ ] `--level` flag filters by log level(s)
- [ ] `--filter` flag supports glob patterns
- [ ] Multiple filters work with AND logic
- [ ] Filtered records not printed or counted
- [ ] Comprehensive unit tests with parameterized cases
- [ ] Edge cases handled gracefully
- [ ] Performance tested with benchmarks
- [ ] Documentation updated with filter examples

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

       # Validate filter patterns
       if config.filter_key_values:
           for key, pattern in config.filter_key_values:
               if not key:
                   errors.append("Empty key in filter")

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

3. **Validation checks:**
   - TOML syntax is valid
   - Required fields present
   - No empty/invalid keys
   - Filter patterns are valid
   - Color codes are valid (if theme support added)

**Acceptance Criteria:**
- [ ] `--validate-config` flag validates TOML syntax
- [ ] Validates dotted keys configuration
- [ ] Validates filter patterns
- [ ] Clear error messages for validation failures
- [ ] Exit code 0 on success, 1 on failure
- [ ] Unit tests for validation logic
- [ ] Documentation with examples

## Testing Strategy

**Approach:** TDD with parameterized tests

1. **Filter predicate tests:**
   ```python
   @pytest.mark.parametrize('record_level,filter_levels,expected', [
       ('error', ['error'], True),
       ('info', ['error'], False),
       ('ERROR', ['error'], True),  # Case insensitive
       ('error', None, True),  # No filter
   ])
   def test_level_filter(record_level, filter_levels, expected):
       # Test implementation
   ```

2. **Glob pattern tests:**
   ```python
   @pytest.mark.parametrize('value,pattern,expected', [
       ('prod-1', 'prod-*', True),
       ('prod-1', 'staging-*', False),
       ('prod-1', 'prod-?', True),
   ])
   def test_glob_matching(value, pattern, expected):
       # Test implementation
   ```

3. **Integration tests:**
   - Process stream with filters
   - Verify correct records pass through
   - Verify filtered records excluded

4. **Config validation tests:**
   - Valid configs pass
   - Invalid TOML fails
   - Empty keys fail
   - Clear error messages

## Performance Considerations

- Filter evaluation should be O(1) or O(k) where k is number of filters
- Use early returns to skip processing filtered records
- Benchmark filtering overhead (<5% impact on throughput)
- Consider caching compiled glob patterns if needed

## Performance Targets

- Filtering adds <5% overhead to processing time
- Glob matching performance acceptable for typical patterns
- Memory usage unchanged

## Deliverables

- [ ] Level filtering implementation
- [ ] Key-value glob filtering implementation
- [ ] Multiple filter AND logic
- [ ] Config validation command
- [ ] Comprehensive test suite (>80% coverage)
- [ ] Benchmarks showing filter performance
- [ ] Documentation with filter examples
- [ ] Updated README with filtering section

## Future Extensions (Not in Phase 3)

- OR logic for filters (e.g., `--filter-or`)
- Regex filtering (Phase 4)
- JQ-style filtering (needs jq dependency)
- Inverse filters (e.g., `--exclude-level`)
