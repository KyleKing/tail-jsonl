# Phase 2: Performance Benchmarking Infrastructure

**Priority:** MEDIUM
**External Dependencies:** `pytest-benchmark` (test dependency only)
**Estimated Complexity:** Medium

## Objectives

Establish performance benchmarking infrastructure to measure throughput, detect regressions, and guide future optimizations. This phase builds the foundation for data-driven performance improvements.

## Features

### 2.4 Add Performance Benchmarks

**Goal:** Create comprehensive benchmark suite using pytest-benchmark

**Benchmark Scenarios:**

1. **Simple logs** (1-5 keys)
   - Minimal overhead baseline
   - Fast path validation

2. **Complex logs** (20+ keys, nested objects)
   - Real-world application logs
   - Kubernetes/Docker logs with metadata

3. **High-volume streams** (10K+ lines)
   - Throughput testing
   - Memory usage validation

4. **Dotted notation heavy logs**
   - Measure impact of Phase 1 caching
   - Validate optimization effectiveness

**Metrics to Track:**
- Throughput: lines/second
- Latency: milliseconds/line
- Memory usage: peak RSS
- CPU time

**Implementation Plan:**

1. **Add pytest-benchmark dependency:**
   ```toml
   [tool.poetry.group.dev.dependencies]
   pytest-benchmark = "^4.0.0"
   ```

2. **Create benchmark fixtures:**
   ```python
   # tests/benchmarks/fixtures.py
   @pytest.fixture
   def simple_log():
       return '{"timestamp": "2024-01-01", "message": "test"}'

   @pytest.fixture
   def complex_log():
       # Generate log with 20+ keys, nested objects

   @pytest.fixture
   def log_stream_10k(tmp_path):
       # Generate 10K line file
   ```

3. **Write benchmark tests:**
   ```python
   # tests/benchmarks/test_performance.py
   def test_simple_log_throughput(benchmark, simple_log):
       benchmark(print_record, simple_log, console, config)
   ```

4. **Add CI integration:**
   - Run benchmarks on every PR
   - Compare against baseline
   - Fail if regression > 20%

**Acceptance Criteria:**
- [ ] pytest-benchmark installed in dev dependencies
- [ ] Benchmark suite covering all 4 scenarios
- [ ] Baseline metrics documented
- [ ] CI job running benchmarks
- [ ] Regression detection configured

### 2.5 Profile Real-World Usage

**Goal:** Profile actual log processing to identify bottlenecks

**Tools:**
- `cProfile` (built-in Python profiler)
- `py-spy` (sampling profiler - optional)
- `snakeviz` (visualization - dev dependency)

**Implementation Plan:**

1. **Add profiling utilities:**
   ```toml
   [tool.poetry.group.dev.dependencies]
   snakeviz = "^2.2.0"
   py-spy = { version = "^0.3.14", optional = true }
   ```

2. **Create profiling test data:**
   - Generate realistic log files (1K, 10K, 100K lines)
   - Include mix of simple and complex logs
   - Add logs with dotted notation

3. **Document profiling workflow:**
   ```bash
   # Generate test data
   python scripts/generate_test_logs.py --lines 10000 > large.jsonl

   # Profile with cProfile
   python -m cProfile -o profile.stats -m tail_jsonl.scripts < large.jsonl

   # Visualize
   poetry run snakeviz profile.stats
   ```

4. **Analyze and document findings:**
   - Time spent in `json.loads()` vs formatting
   - `dotted.get()` / `dotted.remove()` overhead
   - `rich_printer()` bottlenecks
   - I/O vs CPU time distribution

**Focus Areas:**
- JSON parsing overhead
- Dotted key processing (validate Phase 1 improvements)
- Rich console rendering
- String formatting operations

**Acceptance Criteria:**
- [ ] Test log generation script created
- [ ] Profiling workflow documented in `docs/development.md`
- [ ] snakeviz added to dev dependencies
- [ ] Initial profiling report with baseline metrics
- [ ] Bottlenecks identified and documented for future phases

## Testing Strategy

**Approach:** Benchmarking as Documentation

1. Benchmarks serve as performance regression tests
2. Use `pytest.mark.parametrize` for different log sizes
3. Store baseline metrics in repository
4. Document expected performance characteristics

**Example Benchmark:**
```python
@pytest.mark.benchmark(group="throughput")
@pytest.mark.parametrize('num_lines', [100, 1000, 10000])
def test_log_processing_throughput(benchmark, num_lines, generate_logs):
    logs = generate_logs(num_lines, complexity='medium')
    benchmark(process_logs, logs)
```

## Performance Targets

- Benchmark suite runs in <30 seconds
- Detect regressions >20%
- Document baseline: X lines/sec on reference hardware
- Profile identifies top 3 bottlenecks

## Deliverables

- [ ] pytest-benchmark integrated with test suite
- [ ] 4 benchmark scenarios implemented and passing
- [ ] Profiling tools and workflow documented
- [ ] Initial profiling report with findings
- [ ] CI job running benchmarks on PRs
- [ ] Baseline metrics documented in README or docs
- [ ] Test log generation utilities

## Notes

This phase establishes the infrastructure needed for data-driven optimization. Future phases will use these benchmarks to validate performance improvements.
