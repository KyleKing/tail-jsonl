"""Timestamp parsing and formatting."""

from __future__ import annotations

import re
from datetime import datetime

_FRACTION_DIGITS = 6
_FRACTION = re.compile(r'\.(\d+)')
_COMPACT_OFFSET = re.compile(r'(?<=\d)([+-])(\d{2})(\d{2})$')


def format_timestamp(timestamp: str, *, local_time: bool, timestamp_format: str | None) -> str:
    """Return the reformatted timestamp, or the original string when nothing can be changed.

    A timestamp that cannot be parsed is always returned verbatim. A parsed timestamp without a UTC
    offset is never converted, because the zone it was written in is unknown.
    """
    parsed = _parse(timestamp)
    if parsed is None:
        return timestamp
    localized = parsed.astimezone() if local_time and parsed.tzinfo is not None else parsed
    if timestamp_format:
        return localized.strftime(timestamp_format)
    return timestamp if localized is parsed else localized.isoformat()


def _parse(timestamp: str) -> datetime | None:
    try:
        return datetime.fromisoformat(_normalize(timestamp))
    except ValueError:
        return None


def _normalize(timestamp: str) -> str:
    """Return an ISO-8601 string accepted by the stricter `fromisoformat` of Python 3.10."""
    text = timestamp.strip()
    if text[-1:] in {'Z', 'z'}:
        text = f'{text[:-1]}+00:00'
    text = _COMPACT_OFFSET.sub(r'\1\2:\3', text)
    return _FRACTION.sub(_pad_fraction, text, count=1)


def _pad_fraction(match: re.Match[str]) -> str:
    return '.' + match.group(1)[:_FRACTION_DIGITS].ljust(_FRACTION_DIGITS, '0')
