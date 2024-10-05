from dataclasses import asdict
from pathlib import Path

from corallium.tomllib import tomllib

from tail_jsonl.scripts import _load_config


def test_create_default_config():
    """Create the default config for the README."""
    example_config = Path(__file__).parent / 'config_default.toml'

    config = _load_config(config_path=str(example_config))

    assert tomllib.loads(example_config.read_text(encoding='utf-8')) == asdict(config)
