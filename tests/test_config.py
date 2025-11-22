from dataclasses import asdict
from pathlib import Path

from corallium.tomllib import tomllib

from tail_jsonl.scripts import _load_config


def test_create_default_config():
    """Create the default config for the README."""
    example_config = Path(__file__).parent / 'config_default.toml'

    config = _load_config(config_path=str(example_config))

    # Exclude runtime and cached fields from config dict
    config_dict = asdict(config)
    # Runtime flags
    config_dict.pop('debug', None)
    # Cached fields
    if 'keys' in config_dict:
        config_dict['keys'].pop('_dotted_keys', None)
    config_dict.pop('_include_re', None)
    config_dict.pop('_exclude_re', None)
    # Phase 3 filter fields (not in default config file)
    config_dict.pop('include_pattern', None)
    config_dict.pop('exclude_pattern', None)
    config_dict.pop('field_selectors', None)
    config_dict.pop('case_insensitive', None)
    # Phase 7 context fields
    config_dict.pop('context_before', None)
    config_dict.pop('context_after', None)

    assert tomllib.loads(example_config.read_text(encoding='utf-8')) == config_dict


def test_keys_dotted_cache():
    """Test that dotted keys are properly cached in Keys.__post_init__."""
    from tail_jsonl.config import Keys

    # Test with default keys
    keys = Keys()
    dotted = keys.get_dotted_keys()

    # Default on_own_line includes 'text' (no dot), 'exception' (no dot), 'error.stack' (has dot)
    assert 'error.stack' in dotted
    assert 'text' not in dotted
    assert 'exception' not in dotted
    # Should only contain keys with dots
    assert all('.' in key for key in dotted)

    # Test with custom keys
    custom_keys = Keys(on_own_line=['simple', 'server.hostname', 'app.user.id', 'another'])
    custom_dotted = custom_keys.get_dotted_keys()

    assert custom_dotted == ['server.hostname', 'app.user.id']
    assert 'simple' not in custom_dotted
    assert 'another' not in custom_dotted

    # Test with no dotted keys
    no_dotted_keys = Keys(on_own_line=['key1', 'key2', 'key3'])
    assert no_dotted_keys.get_dotted_keys() == []

    # Test with all dotted keys
    all_dotted_keys = Keys(on_own_line=['a.b', 'c.d', 'e.f.g'])
    assert len(all_dotted_keys.get_dotted_keys()) == 3
