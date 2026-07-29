from dataclasses import asdict
from pathlib import Path
from textwrap import dedent

import pytest
from corallium.tomllib import tomllib

from tail_jsonl.scripts import _load_config


def test_create_default_config():
    """Create the default config for the README."""
    example_config = Path(__file__).parent / 'config_default.toml'

    config = _load_config(config_path=str(example_config))

    # Exclude runtime-only settings that are not part of the example config file
    config_dict = asdict(config)
    config_dict.pop('debug', None)
    config_dict.pop('filters', None)
    config_dict.pop('render', None)
    assert tomllib.loads(example_config.read_text(encoding='utf-8')) == config_dict


def test_default_config_has_no_filters():
    config = _load_config(config_path=None)

    assert config.filters.filters_line is False
    assert config.filters.filters_record is False


@pytest.fixture
def filter_config(tmp_path: Path) -> str:
    pth = tmp_path / 'filters.toml'
    pth.write_text(
        dedent("""
            [filters]
            include = ["payment"]
            exclude = ["healthcheck"]
            field_selectors = ["host=prod"]
            case_insensitive = true
            min_level = "warning"
        """),
        encoding='utf-8',
    )
    return str(pth)


def test_filters_from_config_file(filter_config: str):
    config = _load_config(filter_config)

    assert config.filters.include == ['payment']
    assert config.filters.exclude == ['healthcheck']
    assert config.filters.field_selectors == ['host=prod']
    assert config.filters.case_insensitive is True
    assert config.filters.min_level == 'warning'
    assert config.filters.filters_line is True
    assert config.filters.filters_record is True


def test_cli_overrides_config_file(filter_config: str):
    config = _load_config(
        filter_config,
        include=['refund'],
        field_selectors=['host=dev'],
        min_level='error',
    )

    assert config.filters.include == ['refund']
    assert config.filters.field_selectors == ['host=dev']
    assert config.filters.min_level == 'error'
    assert config.filters.exclude == ['healthcheck']


def test_cli_filters_without_config_file():
    config = _load_config(None, exclude=['noise'], case_insensitive=True)

    assert config.filters.exclude == ['noise']
    assert config.filters.exclude_patterns[0].search('NOISE') is not None


def test_default_config_has_no_render_options():
    config = _load_config(config_path=None)

    assert config.render.formats_timestamp is False
    assert config.render.hides_keys is False


@pytest.fixture
def render_config(tmp_path: Path) -> str:
    pth = tmp_path / 'render.toml'
    pth.write_text(
        dedent("""
            [render]
            local_time = true
            timestamp_format = "%H:%M:%S"
            hidden_keys = ["host", "server.region"]
        """),
        encoding='utf-8',
    )
    return str(pth)


def test_render_from_config_file(render_config: str):
    config = _load_config(render_config)

    assert config.render.local_time is True
    assert config.render.timestamp_format == '%H:%M:%S'
    assert config.render.hidden_keys == ['host', 'server.region']
    assert config.render.formats_timestamp is True
    assert config.render.hides_keys is True


def test_cli_overrides_render_config_file(render_config: str):
    config = _load_config(render_config, timestamp_format='%H:%M', hidden_keys=['request_id'])

    assert config.render.timestamp_format == '%H:%M'
    assert config.render.hidden_keys == ['request_id']
    assert config.render.local_time is True


def test_cli_render_without_config_file():
    config = _load_config(None, local_time=True, hidden_keys=['host'])

    assert config.render.local_time is True
    assert config.render.hides_keys is True
