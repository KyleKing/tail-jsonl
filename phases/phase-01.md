# Phase 1: Foundation - Tests & Caching

**Priority:** HIGH
**External Dependencies:** None (uses existing dependencies)
**Estimated Complexity:** Low-Medium

## Objectives

Establish a solid foundation by completing critical test coverage and implementing high-priority performance improvements with zero new dependencies.

## Features

### 3.4 Complete Planned Tasks - Dotted Key Parsing Tests

**Location:** `tail_jsonl/config.py:22` - TODO comment

**Goal:** Write comprehensive tests for dotted key parsing edge cases

**Test Coverage Required:**
- Keys with dots (e.g., `server.hostname`, `app.user.id`)
- Special characters in keys (e.g., `@timestamp`, `log-level`)
- Nested paths (e.g., `data.request.headers.user-agent`)
- Empty keys and edge cases
- Invalid dotted notation
- Keys that don't exist in the data
- Mixed dotted and non-dotted keys

**Acceptance Criteria:**
- [ ] Add parameterized tests in `tests/test_config.py` covering all edge cases
- [ ] Verify dotted keys are correctly parsed and handled
- [ ] Achieve >80% code coverage for dotted key logic
- [ ] Document expected behavior for edge cases

### 2.2 Cache Dotted Notation Pattern Parsing

**Location:** `tail_jsonl/_private/core.py:76-81`

**Current Issue:**
```python
for dotted_key in config.keys.on_own_line:
    if '.' not in dotted_key:
        continue
    if value := dotted.get(record.data, dotted_key):
        record.data[dotted_key] = value if isinstance(value, str) else str(value)
        dotted.remove(record.data, dotted_key)
```

The `dotted.get()` and `dotted.remove()` likely parse the dotted key pattern on every call, which is inefficient for high-volume log processing.

**Implementation Plan:**

1. **Investigate dotted-notation library:**
   - Check if it supports compiled/cached patterns
   - Review source code for optimization opportunities
   - Consider contributing upstream if needed

2. **Pre-parse dotted keys at Config initialization:**
   - Add `_parsed_dotted_keys` cache to Config class
   - Parse keys once when Config is created
   - Store parsed patterns for reuse

3. **Optimize the processing loop:**
   - Use cached patterns instead of parsing on every line
   - Measure performance improvement with benchmark

**Acceptance Criteria:**
- [ ] Add unit tests for dotted key caching logic
- [ ] Implement caching in Config initialization
- [ ] Update `core.py` to use cached patterns
- [ ] Add benchmark comparing before/after performance
- [ ] Verify correctness with existing tests
- [ ] Document caching behavior in code comments

## Testing Strategy

**Approach:** Test-Driven Development (TDD)

1. Write tests first for dotted key edge cases
2. Implement caching logic with tests for cache behavior
3. Use `pytest.mark.parametrize` for comprehensive edge case coverage
4. Focus on API-level tests (test through `print_record()` and `Config`)
5. Minimize mocking - use real dotted-notation library

**Example Test Structure:**
```python
@pytest.mark.parametrize('dotted_key,record_data,expected', [
    ('server.hostname', {'server': {'hostname': 'prod-1'}}, 'prod-1'),
    ('missing.key', {'other': 'data'}, None),
    # ... more edge cases
])
def test_dotted_key_parsing(dotted_key, record_data, expected):
    # Test implementation
```

## Performance Targets

- Reduce per-line dotted key overhead by 50%+
- No regression in existing functionality
- Maintain or improve throughput (lines/sec)

## Deliverables

- [ ] Comprehensive test suite for dotted key parsing
- [ ] Cached dotted key pattern implementation
- [ ] Performance comparison showing improvement
- [ ] Updated documentation for caching behavior
- [ ] All tests passing with >80% coverage
