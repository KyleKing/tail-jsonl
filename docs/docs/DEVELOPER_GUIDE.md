# Developer Notes

## Local Development

```sh
git clone https://github.com/kyleking/tail-jsonl.git
cd tail-jsonl
poetry install --sync
poetry run calcipy-pack pack.install-extras

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
| File                                      | Statements | Missing | Excluded | Coverage |
|-------------------------------------------|-----------:|--------:|---------:|---------:|
| `tail_jsonl/__init__.py`                  | 4          | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/__init__.py`         | 0          | 0       | 0        | 100.0%   |
| `tail_jsonl/_private/core.py`             | 45         | 1       | 0        | 95.9%    |
| `tail_jsonl/_runtime_type_check_setup.py` | 13         | 0       | 37       | 100.0%   |
| `tail_jsonl/config.py`                    | 23         | 0       | 0        | 100.0%   |
| `tail_jsonl/scripts.py`                   | 16         | 0       | 18       | 94.4%    |
| **Totals**                                | 101        | 1       | 55       | 97.2%    |

Generated on: 2025-08-12
<!-- {cte} -->
