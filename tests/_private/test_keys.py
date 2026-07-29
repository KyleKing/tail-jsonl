from __future__ import annotations

import json
from typing import Any

import pytest
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl._private.keys import hide_keys
from tail_jsonl.config import Config, Render

LINE = json.dumps(
    {
        'timestamp': '2024-03-01T12:30:45Z',
        'level': 'error',
        'message': 'payment failed',
        'host': 'prod-1',
        'server': {'hostname': 'prod-1', 'region': 'us-east'},
    },
)


def render(line: str = LINE, **options: Any) -> str:
    console = Console(log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    print_record(line, console, Config(render=Render(**options)))
    return console.end_capture().strip()


def _hidden(data: dict, keys: list[str]) -> dict:  # type: ignore[type-arg]
    hide_keys(data, Render(hidden_keys=keys).hidden_patterns)
    return data


@pytest.mark.parametrize(
    ('keys', 'expected'),
    [
        ([], {'host': 'prod-1', 'server': {'hostname': 'prod-1'}, 'empty': None}),
        (['host'], {'server': {'hostname': 'prod-1'}, 'empty': None}),
        (['server.hostname'], {'host': 'prod-1', 'server': {}, 'empty': None}),
        (['server'], {'host': 'prod-1', 'empty': None}),
        (['missing'], {'host': 'prod-1', 'server': {'hostname': 'prod-1'}, 'empty': None}),
        (['server.missing'], {'host': 'prod-1', 'server': {'hostname': 'prod-1'}, 'empty': None}),
        (['missing.nested'], {'host': 'prod-1', 'server': {'hostname': 'prod-1'}, 'empty': None}),
        (['empty'], {'host': 'prod-1', 'server': {'hostname': 'prod-1'}}),
        (['host', 'server'], {'empty': None}),
    ],
)
def test_hide_keys(keys: list[str], expected: dict) -> None:  # type: ignore[type-arg]
    data = {'host': 'prod-1', 'server': {'hostname': 'prod-1'}, 'empty': None}

    assert _hidden(data, keys) == expected


def test_hides_keys_flag() -> None:
    assert Render().hides_keys is False
    assert Render(hidden_keys=['host']).hides_keys is True


def test_unparseable_hidden_key() -> None:
    with pytest.raises(ValueError, match='Unparseable dotted key'):
        Render(hidden_keys=['[invalid'])


def test_print_record_hides_a_top_level_key() -> None:
    result = render(hidden_keys=['host'])

    assert 'host=prod-1' not in result
    assert 'payment failed' in result
    assert 'hostname' in result


def test_print_record_hides_a_dotted_key() -> None:
    result = render(hidden_keys=['server.hostname'])

    assert 'hostname' not in result
    assert 'us-east' in result


def test_print_record_hiding_is_a_no_op_for_missing_keys() -> None:
    assert render(hidden_keys=['nope', 'also.missing']) == render()


def test_print_record_cannot_hide_the_canonical_keys() -> None:
    result = render(hidden_keys=['timestamp', 'level', 'message'])

    assert result == render()


def test_hiding_wins_over_promotion() -> None:
    line = json.dumps(
        {
            'level': 'error',
            'message': 'boom',
            'error': {'stack': 'Traceback', 'name': 'SourceError'},
        },
    )

    result = render(line, hidden_keys=['error.stack'])

    assert 'Traceback' not in result
    assert 'error.stack' not in result
    assert 'SourceError' in result


def test_hiding_a_parent_removes_the_promoted_child() -> None:
    line = json.dumps({'level': 'error', 'message': 'boom', 'error': {'stack': 'Traceback'}})

    result = render(line, hidden_keys=['error'])

    assert 'Traceback' not in result
    assert 'error' not in result
