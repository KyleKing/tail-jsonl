# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/tail-jsonl.git
cd tail-jsonl
uv sync --all-extras

# See the available tasks
uv run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
```

### Maintenance

Dependency upgrades can be accomplished with:

```sh
uv lock --upgrade
uv sync --all-extras
```

## Benchmarks

The `benchmarks/` directory is excluded from `testpaths`, so `uv run pytest` never runs it. Measure
per-line rendering cost with:

```sh
uv run pytest benchmarks
```

Two scenarios render through a Rich `Console` bound to an in-memory buffer at a fixed width of 120,
so the numbers reflect formatting cost rather than terminal I/O: a minimal record and a 20+ key
nested record that promotes `error.stack` onto its own line.

For end-to-end lines/sec over 10k generated lines (no fixture is committed, the corpus is built at
runtime):

```sh
uv run python -m benchmarks.throughput
uv run python -m benchmarks.throughput --lines 50000 --repeat 5
```

There is no CI regression gate. These are local measurements used to justify or reject perf work
such as `orjson` or output buffering.

## Publishing

Publishing is automated via GitHub Actions using PyPI Trusted Publishing. Tag creation triggers automated publishing.

```sh
./run release              # Bumps version, creates tag, pushes → triggers publish
./run release --suffix=rc  # For pre-releases
```

### Initial Setup

One-time setup to enable PyPI Trusted Publishing:

**Configure GitHub Environments**

Repository Settings → Environments:
- Create `testpypi` environment (no protection rules)
- Create `pypi` environment with "Required reviewers" enabled

**Register Trusted Publishers**

PyPI: https://pypi.org/manage/project/tail_jsonl/settings/publishing/
- Owner: `kyleking`
- Repository: `tail-jsonl`
- Workflow: `publish.yml`
- Environment: `pypi`
    - Or environment `testpypi` (for [TestPyPI](https://test.pypi.org/manage/account/publishing))

### Manual Publishing

For emergency manual publish:

```sh
export UV_PUBLISH_TOKEN=pypi-...
uv build
uv publish
```

## Current Status

<!-- {cts} COVERAGE -->
| File                                      | Statements | Missing | Excluded | Coverage |
|-------------------------------------------|-----------:|--------:|---------:|---------:|
| `tail_jsonl/__init__.py`                  | 4          | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/__init__.py`         | 0          | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/completions.py`      | 75         | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/core.py`             | 67         | 3       | 0        | 93.4%    |
| `tail_jsonl/_private/filters.py`          | 27         | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/keys.py`             | 17         | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/timestamps.py`       | 77         | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/types.py`            | 8          | 0       | 0        | 100.0%   |
| `tail_jsonl/_runtime_type_check_setup.py` | 13         | 0       | 37       | 100.0%   |
| `tail_jsonl/config.py`                    | 87         | 0       | 0        | 100.0%   |
| `tail_jsonl/scripts.py`                   | 39         | 1       | 28       | 95.3%    |
| **Totals**                                | 414        | 4       | 65       | 98.4%    |

Generated on: 2026-07-29
<!-- {cte} -->
