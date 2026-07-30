"""Timestamp parsing and formatting."""

from __future__ import annotations

import re
from datetime import datetime, timezone, tzinfo
from functools import cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TIME_FORMATS = ('clock', 'iso', 'short')
"""Named formats accepted by `time_format`, which also takes any strftime pattern."""

LOCAL_ZONE = 'local'
UTC_ZONE = 'utc'

_FRACTION_DIGITS = 6
_FRACTION = re.compile(r'\.(\d+)')
_COMPACT_OFFSET = re.compile(r'(?<=\d)([+-])(\d{2})(\d{2})$')
_EPOCH = re.compile(r'\d{9,19}(?:\.\d+)?')
_MILLISECONDS_PER_SECOND = 10**3
_EPOCH_SCALES = (
    (10**17, 10**9),
    (10**14, 10**6),
    (10**11, 10**3),
)
"""Lower bound and divisor per epoch unit, from nanoseconds down to milliseconds."""


def format_timestamp(timestamp: str, *, time_zone: str | None, time_format: str | None) -> str:
    """Return the reformatted timestamp, or the original string when nothing can be changed.

    A timestamp that cannot be parsed is always returned verbatim. A parsed timestamp without a UTC
    offset is never converted to another zone, because the zone it was written in is unknown. An
    epoch number is always rendered as ISO-8601, because the digits alone are unreadable.
    """
    epoch = _parse_epoch(timestamp)
    parsed = epoch
    if parsed is None:
        if not (time_zone or time_format):
            return timestamp
        parsed = _parse_iso(timestamp)
        if parsed is None:
            return timestamp
    localized = _apply_zone(parsed, time_zone) if time_zone else parsed
    if time_format:
        return _apply_format(localized, time_format)
    if localized is not parsed or epoch is not None:
        return localized.isoformat()
    return timestamp


@cache
def resolve_zone(name: str) -> tzinfo | None:
    """Return the target zone, or None to mean whichever zone the system is set to.

    Raises:
        ValueError: when the name is neither `local`, `utc`, nor an IANA zone.

    """
    if name.lower() == LOCAL_ZONE:
        return None
    if name.lower() == UTC_ZONE:
        return timezone.utc
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as err:
        msg = (
            f'Unrecognized time zone {name!r}. Expected {LOCAL_ZONE}, {UTC_ZONE}, or an IANA name such as Europe/Berlin'
        )
        raise ValueError(msg) from err


def _apply_zone(value: datetime, time_zone: str) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(resolve_zone(time_zone))


def _apply_format(value: datetime, time_format: str) -> str:
    if time_format == 'iso':
        return value.isoformat()
    if time_format == 'clock':
        return f'{value:%H:%M:%S}.{value.microsecond // _MILLISECONDS_PER_SECOND:03d}'
    if time_format == 'short':
        return f'{value:%m-%d %H:%M:%S}'
    return value.strftime(time_format)


def _parse_epoch(timestamp: str) -> datetime | None:
    text = timestamp.strip()
    if not _EPOCH.fullmatch(text):
        return None
    return datetime.fromtimestamp(_epoch_seconds(float(text)), tz=timezone.utc)


def _epoch_seconds(value: float) -> float:
    """Return seconds, inferring the unit from the magnitude (seconds through nanoseconds)."""
    for lower_bound, divisor in _EPOCH_SCALES:
        if value >= lower_bound:
            return value / divisor
    return value


def _parse_iso(timestamp: str) -> datetime | None:
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
