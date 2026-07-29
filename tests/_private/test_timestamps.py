from __future__ import annotations

import json
import time
from typing import Any

import pytest
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl._private.timestamps import format_timestamp
from tail_jsonl.config import Config, Render


def render(line: str, **options: Any) -> str:
    console = Console(log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    print_record(line, console, Config(render=Render(**options)))
    return console.end_capture().strip()


@pytest.fixture
def _mountain_time(monkeypatch: pytest.MonkeyPatch):
    if not hasattr(time, 'tzset'):
        pytest.skip('The local timezone cannot be set on this platform')
    monkeypatch.setenv('TZ', 'America/Denver')
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


@pytest.mark.usefixtures('_mountain_time')
@pytest.mark.parametrize(
    'timestamp',
    [
        '2024-03-01T12:30:45+00:00',
        '2024-03-01T12:30:45Z',
        '2024-03-01T12:30:45z',
        '2024-03-01T12:30:45+0000',
        '2024-03-01T12:30:45.123456Z',
        '2024-03-01T12:30:45.123Z',
        '2024-03-01T12:30:45.123456789Z',
        '2024-03-01 12:30:45+00:00',
        '2024-03-01T14:30:45+02:00',
        '  2024-03-01T12:30:45Z  ',
    ],
)
def test_local_time_with_format(timestamp: str) -> None:
    result = format_timestamp(timestamp, local_time=True, timestamp_format='%Y-%m-%d %H:%M:%S')

    assert result == '2024-03-01 05:30:45'


@pytest.mark.usefixtures('_mountain_time')
def test_local_time_without_format() -> None:
    result = format_timestamp('2024-03-01T12:30:45Z', local_time=True, timestamp_format=None)

    assert result == '2024-03-01T05:30:45-07:00'


@pytest.mark.parametrize(
    'timestamp',
    [
        '2024-03-01T12:30:45',
        '2024-03-01T12:30:45.123456',
        '2024-03-01',
    ],
)
def test_naive_timestamps_are_never_converted(timestamp: str) -> None:
    assert format_timestamp(timestamp, local_time=True, timestamp_format=None) == timestamp


def test_naive_timestamp_is_still_formatted() -> None:
    result = format_timestamp('2024-03-01T12:30:45', local_time=True, timestamp_format='%H:%M')

    assert result == '12:30'


@pytest.mark.parametrize(
    'timestamp',
    [
        '<no timestamp>',
        '',
        'not a timestamp',
        '2024-13-45T99:99:99',
        'Mar 01 2024 12:30:45',
        '1709296245',
        '2024-03-01T12:30:45+99:99',
        '[2024-03-01]',
    ],
)
@pytest.mark.parametrize('timestamp_format', [None, '%H:%M:%S'])
def test_unparseable_timestamps_pass_through(timestamp: str, timestamp_format: str | None) -> None:
    result = format_timestamp(timestamp, local_time=True, timestamp_format=timestamp_format)

    assert result == timestamp


def test_format_without_local_time() -> None:
    result = format_timestamp('2024-03-01T12:30:45Z', local_time=False, timestamp_format='%H:%M:%S')

    assert result == '12:30:45'


def test_no_options_leaves_the_timestamp_untouched() -> None:
    timestamp = '  2024-03-01T12:30:45Z '

    assert format_timestamp(timestamp, local_time=False, timestamp_format=None) == timestamp


def test_render_flags_default_to_disabled() -> None:
    render_config = Render()

    assert render_config.formats_timestamp is False
    assert render_config.hides_keys is False


@pytest.mark.parametrize(
    ('render_config', 'expected'),
    [
        (Render(local_time=True), True),
        (Render(timestamp_format='%H:%M'), True),
        (Render(hidden_keys=['host']), False),
    ],
)
def test_formats_timestamp_flag(render_config: Render, *, expected: bool) -> None:
    assert render_config.formats_timestamp is expected


@pytest.mark.usefixtures('_mountain_time')
def test_print_record_local_time() -> None:
    line = json.dumps({'timestamp': '2024-03-01T12:30:45Z', 'level': 'info', 'message': 'hi'})

    assert render(line, local_time=True, timestamp_format='%H:%M:%S').startswith('05:30:45')


def test_print_record_keeps_unparseable_timestamp() -> None:
    line = json.dumps({'timestamp': 'yesterday', 'level': 'info', 'message': 'hi'})

    assert render(line, local_time=True, timestamp_format='%H:%M:%S').startswith('yesterday')


def test_print_record_missing_timestamp_is_not_formatted() -> None:
    assert render('{"message": "hi"}', local_time=True, timestamp_format='%H:%M:%S').startswith('<no timestamp>')


def test_print_record_default_matches_the_raw_timestamp() -> None:
    line = json.dumps({'timestamp': '2024-03-01T12:30:45Z', 'level': 'info', 'message': 'hi'})

    assert render(line).startswith('2024-03-01T12:30:45Z')
