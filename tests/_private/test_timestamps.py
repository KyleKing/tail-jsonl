from __future__ import annotations

import json
import time
from typing import Any

import pytest
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl._private.timestamps import format_timestamp, resolve_zone
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
def test_local_zone_with_format(timestamp: str) -> None:
    result = format_timestamp(timestamp, time_zone='local', time_format='%Y-%m-%d %H:%M:%S')

    assert result == '2024-03-01 05:30:45'


@pytest.mark.usefixtures('_mountain_time')
def test_local_zone_without_format() -> None:
    result = format_timestamp('2024-03-01T12:30:45Z', time_zone='local', time_format=None)

    assert result == '2024-03-01T05:30:45-07:00'


def test_utc_zone() -> None:
    result = format_timestamp('2024-03-01T14:30:45+02:00', time_zone='utc', time_format=None)

    assert result == '2024-03-01T12:30:45+00:00'


def test_named_zone() -> None:
    try:
        resolve_zone('Europe/Berlin')
    except ValueError:
        pytest.skip('The IANA timezone database is unavailable')

    result = format_timestamp('2024-03-01T12:30:45Z', time_zone='Europe/Berlin', time_format=None)

    assert result == '2024-03-01T13:30:45+01:00'


def test_unrecognized_zone() -> None:
    with pytest.raises(ValueError, match='Unrecognized time zone'):
        resolve_zone('Mars/Olympus_Mons')


@pytest.mark.parametrize(
    ('time_format', 'expected'),
    [
        ('iso', '2024-03-01T12:30:45.123000+00:00'),
        ('clock', '12:30:45.123'),
        ('short', '03-01 12:30:45'),
        ('%H:%M', '12:30'),
    ],
)
def test_time_formats(time_format: str, expected: str) -> None:
    result = format_timestamp('2024-03-01T12:30:45.123Z', time_zone=None, time_format=time_format)

    assert result == expected


@pytest.mark.parametrize(
    ('timestamp', 'expected'),
    [
        ('1709296245', '2024-03-01T12:30:45+00:00'),
        ('1709296245123', '2024-03-01T12:30:45.123000+00:00'),
        ('1709296245123456', '2024-03-01T12:30:45.123456+00:00'),
        ('1709296245.123', '2024-03-01T12:30:45.123000+00:00'),
    ],
)
def test_epoch_is_always_rendered_as_iso(timestamp: str, expected: str) -> None:
    assert format_timestamp(timestamp, time_zone=None, time_format=None) == expected


def test_epoch_nanoseconds() -> None:
    result = format_timestamp('1709296245123456789', time_zone=None, time_format=None)

    assert result.startswith('2024-03-01T12:30:45')


def test_epoch_respects_the_zone_and_format() -> None:
    result = format_timestamp('1709296245123', time_zone='utc', time_format='clock')

    assert result == '12:30:45.123'


@pytest.mark.parametrize('timestamp', ['12345678', '1', '0'])
def test_short_numbers_are_not_treated_as_epochs(timestamp: str) -> None:
    assert format_timestamp(timestamp, time_zone=None, time_format=None) == timestamp


@pytest.mark.parametrize(
    'timestamp',
    [
        '2024-03-01T12:30:45',
        '2024-03-01T12:30:45.123456',
        '2024-03-01',
    ],
)
def test_naive_timestamps_are_never_converted(timestamp: str) -> None:
    assert format_timestamp(timestamp, time_zone='local', time_format=None) == timestamp


def test_naive_timestamp_is_still_formatted() -> None:
    result = format_timestamp('2024-03-01T12:30:45', time_zone='local', time_format='%H:%M')

    assert result == '12:30'


@pytest.mark.parametrize(
    'timestamp',
    [
        '<no timestamp>',
        '',
        'not a timestamp',
        '2024-13-45T99:99:99',
        'Mar 01 2024 12:30:45',
        '2024-03-01T12:30:45+99:99',
        '[2024-03-01]',
    ],
)
@pytest.mark.parametrize('time_format', [None, '%H:%M:%S'])
def test_unparseable_timestamps_pass_through(timestamp: str, time_format: str | None) -> None:
    result = format_timestamp(timestamp, time_zone='local', time_format=time_format)

    assert result == timestamp


def test_format_without_a_zone() -> None:
    result = format_timestamp('2024-03-01T12:30:45Z', time_zone=None, time_format='%H:%M:%S')

    assert result == '12:30:45'


def test_no_options_leaves_the_timestamp_untouched() -> None:
    timestamp = '  2024-03-01T12:30:45Z '

    assert format_timestamp(timestamp, time_zone=None, time_format=None) == timestamp


def test_render_flags_default_to_disabled() -> None:
    render_config = Render()

    assert render_config.hides_keys is False


def test_render_rejects_an_unknown_zone() -> None:
    with pytest.raises(ValueError, match='Unrecognized time zone'):
        Render(time_zone='Mars/Olympus_Mons')


@pytest.mark.usefixtures('_mountain_time')
def test_print_record_local_zone() -> None:
    line = json.dumps({'timestamp': '2024-03-01T12:30:45Z', 'level': 'info', 'message': 'hi'})

    assert render(line, time_zone='local', time_format='%H:%M:%S').startswith('05:30:45')


def test_print_record_keeps_unparseable_timestamp() -> None:
    line = json.dumps({'timestamp': 'yesterday', 'level': 'info', 'message': 'hi'})

    assert render(line, time_zone='local', time_format='%H:%M:%S').startswith('yesterday')


def test_print_record_missing_timestamp_is_not_formatted() -> None:
    assert render('{"message": "hi"}', time_zone='local', time_format='%H:%M:%S').startswith('<no timestamp>')


def test_print_record_default_matches_the_raw_timestamp() -> None:
    line = json.dumps({'timestamp': '2024-03-01T12:30:45Z', 'level': 'info', 'message': 'hi'})

    assert render(line).startswith('2024-03-01T12:30:45Z')


def test_print_record_converts_a_pino_epoch_without_configuration() -> None:
    assert render('{"time":1709296245123,"level":"info","msg":"hi"}').startswith('2024-03-01T12:30:45.123')
