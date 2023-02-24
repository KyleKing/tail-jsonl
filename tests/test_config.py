from pathlib import Path

import tomli_w
from corallium.tomllib import tomllib  # type: ignore[no-redef]

from tail_jsonl.config import Config


def test_create_default_config():
    """Create the default config for the README."""
    expected_config = Path(__file__).parent / 'config_default.toml'

    config = tomli_w.dumps(Config().dict())

    assert tomllib.loads(expected_config.read_text(encoding='utf-8')) == tomllib.loads(config), config
