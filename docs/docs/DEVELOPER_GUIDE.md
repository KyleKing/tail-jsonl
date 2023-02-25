# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/tail-jsonl.git
cd tail-jsonl
poetry install --sync

# See the available tasks
poetry run calcipy
# Or use a local 'run' file (so that 'calcipy' can be extended)
./run

# Run the default task list (lint, auto-format, test coverage, etc.)
./run main

# Make code changes and run specific tasks as needed:
./run lint.fix test
```

## Publishing

For testing, create an account on [TestPyPi](https://test.pypi.org/legacy/). Replace `...` with the API token generated on TestPyPi or PyPi respectively

```sh
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi ...

./run main pack.publish --to-test-pypi
# If you didn't configure a token, you will need to provide your username and password to publish
```

To publish to the real PyPi

```sh
poetry config pypi-token.pypi ...
./run release

# Or for a pre-release
./run release --suffix=rc
```

## Current Status

<!-- {cts} COVERAGE -->
| File                              |   Statements |   Missing |   Excluded | Coverage   |
|-----------------------------------|--------------|-----------|------------|------------|
| `tail_jsonl/__init__.py`          |            3 |         0 |          0 | 100.0%     |
| `tail_jsonl/_private/__init__.py` |            0 |         0 |          0 | 100.0%     |
| `tail_jsonl/_private/core.py`     |           49 |         1 |          0 | 98.0%      |
| `tail_jsonl/config.py`            |           11 |         0 |          0 | 100.0%     |
| `tail_jsonl/scripts.py`           |           18 |         0 |         11 | 100.0%     |
| **Totals**                        |           81 |         1 |         11 | 98.8%      |

Generated on: 2023-02-25
<!-- {cte} -->
