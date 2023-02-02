from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl.main import _load_config

from .configuration import TEST_DATA_DIR


def test_core_escapping_dot_notation(console: Console):
    config = _load_config(str(TEST_DATA_DIR / 'test-dot-notation.toml'))
    print_record('{"this.message": "this-dot-message", "this.key": "key"}', console, config)

    result = console.end_capture()

    assert result.strip() == '<no timestamp>               <no level> this-dot-message     this.key: key'
