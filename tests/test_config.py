from pathlib import Path

import tomli_w

from tail_jsonl.config import Config

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def test_create_default_config():
    """Create the default config for the README."""
    expected_config = Path(__file__).parent / 'config_default.toml'

    config = tomli_w.dumps(Config().dict())

    assert tomllib.loads(expected_config.read_text()) == tomllib.loads(config)
