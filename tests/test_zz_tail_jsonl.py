"""Final test alphabetically (zz) to catch general integration cases."""

from pathlib import Path

from tail_jsonl import __version__

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def test_version():
    """Check that PyProject and __version__ are equivalent."""
    data = Path('pyproject.toml').read_text(encoding='utf-8')

    result = tomllib.loads(data)['tool']['poetry']['version']

    assert result == __version__
