# Phase 9: Documentation & CI Polish

**Priority:** MEDIUM
**External Dependencies:** None
**Estimated Complexity:** Low-Medium

## Objectives

Final polish phase to improve documentation, optimize CI pipeline, and evaluate remaining performance opportunities. This phase ensures the project is well-maintained, discoverable, and efficient.

## Features

### 3.7 CI Efficiency Improvements

**Goal:** Optimize GitHub Actions workflow for faster feedback

**Current State:**
- Tests run on 3 different jobs: lint, test, typecheck
- Jobs run in parallel (good)
- Python 3.10+ tested

**Optimization Opportunities:**

1. **Cache Poetry virtualenv across jobs:**
   ```yaml
   # .github/workflows/test.yml
   - name: Cache Poetry virtualenv
     uses: actions/cache@v3
     with:
       path: |
         ~/.cache/pypoetry
         .venv
       key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
       restore-keys: |
         ${{ runner.os }}-poetry-
   ```

2. **Verify jobs run in parallel:**
   - Already done, but confirm no dependencies between jobs
   - Check job timing to ensure efficient parallelization

3. **Add benchmark job (from Phase 2):**
   ```yaml
   benchmark:
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v3
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       - name: Install dependencies
         run: |
           pip install poetry
           poetry install --sync
       - name: Run benchmarks
         run: poetry run pytest tests/benchmarks/ --benchmark-only
       - name: Compare with baseline
         run: |
           # Compare against stored baseline
           # Fail if regression > 20%
   ```

4. **Conditional jobs for documentation:**
   - Only run doc builds when docs/ changes
   - Skip expensive jobs on draft PRs

**Implementation Plan:**

1. Update `.github/workflows/test.yml` with caching
2. Add benchmark job
3. Verify parallel execution
4. Document CI setup in CONTRIBUTING.md

**Acceptance Criteria:**
- [ ] Poetry virtualenv cached across jobs
- [ ] Benchmark job added (if Phase 2 completed)
- [ ] Jobs run in parallel
- [ ] CI run time optimized
- [ ] Documentation updated

### 3.8 Documentation Maintenance

**Goal:** Update and expand documentation for discoverability and usability

**Areas Needing Attention:**

1. **Update Alternatives List (README.md:14):**
   - Research latest JSON log viewers
   - Add newly popular tools:
     - `hl` - Fast log viewer in Rust
     - `fblog` - Small command-line JSON log viewer
     - `jl` - JSON logs viewer
     - `bunyan` - Node.js JSON logger viewer
   - Compare features vs tail-jsonl
   - Add comparison table

   ```markdown
   ## Alternatives

   | Tool | Language | Features | When to use |
   |------|----------|----------|-------------|
   | tail-jsonl | Python | Filtering, highlighting, stats | General-purpose, Python ecosystem |
   | hl | Rust | Very fast | Performance-critical, large logs |
   | fblog | Rust | Minimal, fast | Simple filtering |
   | jq | C | Powerful querying | Complex transformations |
   | angle-grinder | Rust | Aggregations | Log analysis |
   ```

2. **Configuration Examples:**

   Add section to README or docs/ with common use cases:

   ```markdown
   ## Configuration Examples

   ### Kubernetes/stern logs

   ```toml
   # ~/.tail-jsonl.toml
   [keys]
   on_own_line = ["namespace", "pod", "container"]

   [keys.keep]
   timestamp = true
   level = true
   message = true
   ```

   ### Docker Compose logs

   ```toml
   [keys]
   on_own_line = ["container_name", "service"]

   [keys.keep]
   timestamp = true
   message = true
   ```

   ### Application logs with structured errors

   ```toml
   [keys]
   on_own_line = [
       "error.code",
       "error.message",
       "user.id",
       "request.id",
   ]
   ```

3. **Troubleshooting Section:**

   Add to README or separate TROUBLESHOOTING.md:

   ```markdown
   ## Troubleshooting

   ### Performance Tuning

   **Problem:** Slow processing on large log files

   **Solutions:**
   - Use `--stats` to measure throughput
   - Disable features you don't need (e.g., `--no-time`)
   - Filter early with `--level` or `--filter`
   - Consider buffering: `tail -f logs.jsonl | tail-jsonl`

   ### Character Encoding Issues

   **Problem:** Garbled characters or encoding errors

   **Solutions:**
   - Ensure logs are UTF-8 encoded
   - Set `PYTHONIOENCODING=utf-8` environment variable
   - Use `iconv` to convert: `iconv -f ISO-8859-1 -t UTF-8 logs.jsonl | tail-jsonl`

   ### Color Display Problems

   **Problem:** No colors or wrong colors in terminal

   **Solutions:**
   - Check terminal supports colors: `echo $TERM`
   - Try different theme: `tail-jsonl --theme=light`
   - Force color output: `tail-jsonl --force-color`
   - Disable colors: `tail-jsonl --theme=none`

   ### Parse Errors

   **Problem:** Many parse errors in `--stats`

   **Solutions:**
   - Verify logs are valid JSON (one object per line)
   - Check for multi-line logs (not supported)
   - Use `--stats` to see error percentage
   - Preprocess with `jq -c` to compact JSON
   ```

4. **Development Documentation:**

   Create or update `docs/development.md`:

   ```markdown
   ## Development Guide

   ### Setup

   ```bash
   poetry install --sync
   poetry run calcipy-pack pack.install-extras
   ```

   ### Running Tests

   ```bash
   # All tests
   poetry run pytest tests/ -v

   # With coverage
   poetry run pytest tests/ --cov=tail_jsonl --cov-report=html

   # Benchmarks
   poetry run pytest tests/benchmarks/ --benchmark-only
   ```

   ### Code Quality

   ```bash
   # Linting
   poetry run ruff check . --fix

   # Formatting
   poetry run ruff format .

   # Type checking
   poetry run mypy .
   ```

   ### Profiling

   See Phase 2 profiling documentation...
   ```

5. **Feature Documentation:**

   Update README with new features from each phase:
   - Filtering (Phase 3)
   - Search/highlighting (Phase 4)
   - Statistics (Phase 5)
   - Timestamp formatting (Phase 6)
   - Context lines (Phase 7)
   - Themes (Phase 8)

**Implementation Plan:**

1. Research and update alternatives list
2. Add configuration examples section
3. Create troubleshooting section
4. Update/create development docs
5. Document new features as phases complete
6. Add badges for CI, coverage, PyPI version

**Acceptance Criteria:**
- [ ] Alternatives list updated with latest tools
- [ ] Configuration examples for 3+ common use cases
- [ ] Troubleshooting section with 5+ common issues
- [ ] Development documentation complete
- [ ] All new features documented
- [ ] README badges updated
- [ ] Links verified

### 2.6 Consider Line Buffering Optimizations

**Goal:** Evaluate and implement line buffering optimizations if beneficial

**Current State:**
```python
with fileinput.input() as _f:
    for line in _f:
        print_record(line, console, config)
```

**Potential Optimizations:**

1. **Batch processing of lines:**
   - If Rich console supports batching, process N lines at once
   - Research: Does Rich benefit from batching?

2. **Pre-allocate buffers:**
   - Reuse string buffers
   - Reduce memory allocations

3. **Use sys.stdin.buffer for binary I/O:**
   - If encoding is known, read binary and decode once
   - May be faster than text I/O

**Investigation Required:**

1. Profile current I/O vs CPU time split
2. Benchmark batch processing vs line-by-line
3. Test binary I/O performance
4. Measure memory allocation overhead

**Decision Matrix:**

| Optimization | Benefit | Complexity | Worth It? |
|--------------|---------|------------|-----------|
| Batch processing | Low (I/O dominates) | Medium | Probably not |
| Buffer reuse | Low | Low | Maybe |
| Binary I/O | Low | Medium | Probably not |

**Acceptance Criteria:**
- [ ] Profiling shows I/O vs CPU time split
- [ ] Batch processing benchmarked
- [ ] Binary I/O benchmarked
- [ ] Decision documented: implement or skip
- [ ] If implemented: tests and benchmarks
- [ ] If skipped: rationale documented

**Expected Outcome:**
Likely negligible impact since I/O dominates CPU time. Document findings and skip implementation unless profiling shows otherwise.

## Testing Strategy

**CI Improvements:**
- Manual verification of workflow changes
- Monitor CI run times before/after
- Ensure caching works correctly

**Documentation:**
- Link checker to verify no broken links
- Manual review of examples
- Spell check with tool like `codespell`

**Line Buffering:**
- Benchmark before/after
- Compare throughput metrics
- Memory profiling

## Deliverables

### CI Improvements
- [ ] Poetry cache configured
- [ ] Benchmark job added (if Phase 2 complete)
- [ ] Parallel execution verified
- [ ] CI run time improved
- [ ] Documentation updated

### Documentation
- [ ] Alternatives list updated
- [ ] 3+ configuration examples added
- [ ] Troubleshooting section with 5+ issues
- [ ] Development guide complete
- [ ] All features documented
- [ ] README badges updated
- [ ] Links verified

### Line Buffering
- [ ] Profiling completed
- [ ] Benchmarks run
- [ ] Decision made and documented
- [ ] Implementation (if beneficial) or rationale (if skipped)

## Future Extensions (Not in Phase 9)

- Interactive mode documentation
- Video tutorials/demos
- Blog post about architecture
- Conference talk
- Integration examples with other tools (stern, docker-compose, etc.)

## Dependencies

- `codespell` (optional, for spell checking)
- No runtime dependencies

## Notes

This is the final polish phase. Focus on making the project accessible to new users and maintainable for future contributors.

## Priority Order

Within Phase 9, prioritize:

1. **HIGH:** Documentation updates (helps users immediately)
2. **MEDIUM:** CI improvements (helps development velocity)
3. **LOW:** Line buffering evaluation (likely skippable)

Start with documentation since it has immediate user value.
