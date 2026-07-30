from __future__ import annotations

import json
import re
from typing import Any

import pytest
from rich.console import Console

from tail_jsonl._private.core import print_record
from tail_jsonl._private.filters import line_passes, record_passes
from tail_jsonl._private.types import Record
from tail_jsonl.config import Config, Filters

LINE = json.dumps({'level': 'error', 'message': 'payment failed', 'host': 'prod-1'})


def make_record(
    timestamp: str = '2024-01-01T00:00:00',
    level: str = 'INFO',
    message: str = 'test message',
    **data: Any,
) -> Record:
    return Record(timestamp=timestamp, level=level, message=message, data=dict(data))


def render(line: str, **filters: Any) -> str:
    console = Console(log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    print_record(line, console, Config(filters=Filters(**filters)))
    return console.end_capture().strip()


@pytest.mark.parametrize(
    ('include', 'exclude', 'expected'),
    [
        ([], [], True),
        (['payment'], [], True),
        (['success'], [], False),
        (['success', 'payment'], [], True),
        ([], ['payment'], False),
        ([], ['success'], True),
        ([], ['success', 'payment'], False),
        (['payment'], ['prod-1'], False),
        (['payment'], ['dev-1'], True),
        (['success'], ['dev-1'], False),
        (['error|warning'], [], True),
    ],
)
def test_line_passes(include: list[str], exclude: list[str], *, expected: bool) -> None:
    filters = Filters(include=include, exclude=exclude)

    assert line_passes(LINE, filters) is expected


@pytest.mark.parametrize(
    ('pattern', 'case_insensitive', 'expected'),
    [
        ('PAYMENT', False, False),
        ('PAYMENT', True, True),
        ('payment', False, True),
    ],
)
def test_line_case_insensitivity(pattern: str, *, case_insensitive: bool, expected: bool) -> None:
    filters = Filters(include=[pattern], case_insensitive=case_insensitive)

    assert line_passes(LINE, filters) is expected


@pytest.mark.parametrize(
    ('selectors', 'expected'),
    [
        ([], True),
        (['host=prod-1'], True),
        (['host=prod-'], True),
        (['host=^prod-1$'], True),
        (['host=dev'], False),
        (['missing=anything'], False),
        (['host=prod', 'level=ERROR'], True),
        (['host=prod', 'level=INFO'], False),
        (['level=ERROR'], True),
        (['message=payment'], True),
        (['timestamp=2024-'], True),
        (['server.hostname=prod-1'], True),
        (['server.hostname=dev'], False),
        (['app.user.id=123'], True),
        (['app.user.missing=123'], False),
        (['host.missing=123'], False),
        (['count=42'], True),
    ],
)
def test_record_passes_field_selectors(selectors: list[str], *, expected: bool) -> None:
    record = make_record(
        timestamp='2024-01-01',
        level='ERROR',
        message='payment failed',
        host='prod-1',
        count=42,
        server={'hostname': 'prod-1'},
        app={'user': {'id': 123}},
    )

    assert record_passes(record, Filters(field_selectors=selectors)) is expected


def test_record_field_selector_case_insensitivity() -> None:
    record = make_record(host='PROD-1')

    assert record_passes(record, Filters(field_selectors=['host=prod'])) is False
    assert record_passes(record, Filters(field_selectors=['host=prod'], case_insensitive=True)) is True


@pytest.mark.parametrize(
    ('level', 'min_level', 'expected'),
    [
        ('debug', 'info', False),
        ('info', 'info', True),
        ('warning', 'info', True),
        ('ERROR', 'info', True),
        ('error', 'error', True),
        ('warn', 'error', False),
        ('', 'error', True),
        ('unrecognized', 'error', True),
        ('trace', 'error', False),
        ('trace', 'trace', True),
        ('debug', 'trace', True),
        ('notice', 'info', True),
        ('notice', 'warning', False),
        ('critical', 'error', True),
        ('fatal', 'error', True),
        ('error', 'critical', False),
        ('info', None, True),
    ],
)
def test_record_passes_min_level(level: str, min_level: str | None, *, expected: bool) -> None:
    record = make_record(level=level)

    assert record_passes(record, Filters(min_level=min_level)) is expected


def test_min_level_combines_with_field_selector() -> None:
    record = make_record(level='error', host='prod-1')

    assert record_passes(record, Filters(min_level='warning', field_selectors=['host=prod'])) is True
    assert record_passes(record, Filters(min_level='warning', field_selectors=['host=dev'])) is False
    assert record_passes(record, Filters(min_level='critical', field_selectors=['host=prod'])) is False


def test_filters_flags_default_to_disabled() -> None:
    filters = Filters()

    assert filters.filters_line is False
    assert filters.filters_record is False


@pytest.mark.parametrize(
    ('filters', 'line_enabled', 'record_enabled'),
    [
        (Filters(include=['a']), True, False),
        (Filters(exclude=['a']), True, False),
        (Filters(field_selectors=['a=b']), False, True),
        (Filters(min_level='info'), False, True),
    ],
)
def test_filters_flags(filters: Filters, *, line_enabled: bool, record_enabled: bool) -> None:
    assert filters.filters_line is line_enabled
    assert filters.filters_record is record_enabled


def test_invalid_pattern() -> None:
    with pytest.raises(re.error):
        Filters(include=['[invalid('])


def test_invalid_field_selector() -> None:
    with pytest.raises(ValueError, match='KEY=PATTERN'):
        Filters(field_selectors=['no-equals-sign'])


def test_invalid_min_level() -> None:
    with pytest.raises(ValueError, match='Unrecognized level'):
        Filters(min_level='loud')


def test_print_record_no_filters() -> None:
    assert render(LINE) == '<no timestamp>               [ERROR  ] payment failed host=prod-1'


def test_print_record_include() -> None:
    assert render(LINE, include=['payment']) == render(LINE)
    assert not render(LINE, include=['success'])


def test_print_record_exclude() -> None:
    assert not render(LINE, exclude=['payment'])
    assert render(LINE, exclude=['success']) == render(LINE)


def test_print_record_field_selector() -> None:
    assert not render(LINE, field_selectors=['host=dev'])
    assert render(LINE, field_selectors=['host=prod']) == render(LINE)


def test_print_record_min_level() -> None:
    assert not render(LINE, min_level='critical')
    assert render(LINE, min_level='warning') == render(LINE)


def test_unparseable_line_respects_raw_patterns() -> None:
    assert not render('not json at all\n', exclude=['json'])
    assert not render('not json at all\n', include=['nope'])
    assert render('not json at all\n', include=['json']) == 'not json at all'


def test_unparseable_line_survives_record_filters() -> None:
    line = 'not json at all\n'

    result = render(line, field_selectors=['host=dev'], min_level='critical')

    assert result == 'not json at all'
