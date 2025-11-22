"""Filtering logic for log records (Phase 3 - Stern-Aligned)."""

from __future__ import annotations

from fnmatch import fnmatch

import dotted  # type: ignore[import-untyped]

from tail_jsonl._private.core import Record
from tail_jsonl.config import Config


def should_include_record(
    record: Record,
    formatted_output: str,
    config: Config,
) -> bool:
    """Return True if record passes all filters.

    Filters are applied in order:
    1. Field selectors (applied to extracted fields)
    2. Include pattern (allowlist - applied to formatted output)
    3. Exclude pattern (blocklist - applied to formatted output)

    All filters use AND logic - record must pass all filters to be included.

    Args:
        record: Parsed log record
        formatted_output: The formatted string that will be displayed
        config: Configuration with filter settings

    Returns:
        True if record should be included, False otherwise
    """
    # Field selectors (applied to extracted fields before formatting)
    if config.field_selectors:
        for key, pattern in config.field_selectors:
            value = _get_field_value(record, key)

            if value is None:
                return False  # Key doesn't exist, exclude record

            # Match against pattern (glob, case-insensitive)
            if not fnmatch(str(value).lower(), pattern.lower()):
                return False

    # Include pattern (allowlist - applied to formatted output)
    if config._include_re:
        if not config._include_re.search(formatted_output):
            return False

    # Exclude pattern (blocklist - applied to formatted output)
    if config._exclude_re:
        if config._exclude_re.search(formatted_output):
            return False

    return True


def _get_field_value(record: Record, key: str) -> str | None:
    """Get field value from record, supporting dotted keys.

    Args:
        record: Parsed log record
        key: Field key (may be dotted, e.g., 'log.level')

    Returns:
        Field value as string, or None if not found
    """
    # Try standard extracted fields first
    if key == 'timestamp':
        return record.timestamp
    if key == 'level':
        return record.level
    if key == 'message':
        return record.message

    # Check in data dict (supports dotted keys)
    if '.' in key:
        # Use dotted notation for nested keys
        value = dotted.get(record.data, key)
    else:
        # Simple key lookup
        value = record.data.get(key)

    return str(value) if value is not None else None
