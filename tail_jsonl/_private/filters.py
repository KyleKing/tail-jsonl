"""Predicates for dropping input before it is rendered."""

from __future__ import annotations

import logging
import re

import dotted  # type: ignore[import-untyped]
from corallium.loggers.styles import get_level

from tail_jsonl._private.types import Record
from tail_jsonl.config import Filters


def line_passes(line: str, filters: Filters) -> bool:
    """Return True when the raw line should be parsed and rendered."""
    if any(pattern.search(line) for pattern in filters.exclude_patterns):
        return False
    return not filters.include_patterns or any(pattern.search(line) for pattern in filters.include_patterns)


def record_passes(record: Record, filters: Filters) -> bool:
    """Return True when the parsed record should be rendered."""
    if not _level_passes(record, filters.min_level_value):
        return False
    return all(_selector_matches(record, key, pattern) for key, pattern in filters.selector_patterns)


def _level_passes(record: Record, min_level_value: int) -> bool:
    level = get_level(name=record.level)
    return level == logging.NOTSET or level >= min_level_value


def _selector_matches(record: Record, key: str, pattern: re.Pattern[str]) -> bool:
    value = _field_value(record, key)
    return value is not None and bool(pattern.search(value))


def _field_value(record: Record, key: str) -> str | None:
    promoted = {'level': record.level, 'message': record.message, 'timestamp': record.timestamp}
    if promoted.get(key):
        return promoted[key]
    value = dotted.get(record.data, key)
    return None if value is None else str(value)
