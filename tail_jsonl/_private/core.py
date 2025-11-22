"""Core print logic."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import dotted  # type: ignore[import-untyped]
from corallium.loggers.rich_printer import rich_printer
from corallium.loggers.styles import get_level
from rich.console import Console

from tail_jsonl.config import Config


def _dot_pop(data: dict, key: str) -> str | None:  # type: ignore[type-arg]
    value = dotted.get(data, key)
    if isinstance(value, str):
        dotted.remove(data, key)
        return value or None
    if isinstance(value, list):
        dotted.remove(data, key)
        return str(value)
    return None


def _pop_key(data: dict, keys: list[str], index: int, fallback: str) -> Any:  # type: ignore[type-arg]
    """Return result of recursively searching for a matching key."""
    if index >= len(keys):
        return fallback
    key = keys[index]
    return _dot_pop(data, key) or _pop_key(data, keys, index + 1, fallback)


def pop_key(data: dict, keys: list[str], fallback: str) -> Any:  # type: ignore[type-arg]
    """Return the first key in the data or default to the fallback."""
    return _pop_key(data, keys, 0, fallback)


@dataclass
class Record:
    """Record Model."""

    timestamp: str
    level: str
    message: str
    data: dict  # type: ignore[type-arg]

    @classmethod
    def from_line(cls, data: dict, config: Config) -> Record:  # type: ignore[type-arg]
        """Return Record from jsonl."""
        return cls(
            timestamp=pop_key(data, config.keys.timestamp, '<no timestamp>'),
            level=pop_key(data, config.keys.level, ''),
            message=pop_key(data, config.keys.message, '<no message>'),
            data=data,
        )


def check_if_match(line: str, console: Console, config: Config) -> bool:
    """Check if line matches filters without printing.

    Args:
        line: Raw input line to check
        console: Rich console for output capture
        config: Configuration settings

    Returns:
        True if line would pass filters, False otherwise
    """
    # If no filters are configured, everything matches
    if not (config._include_re or config._exclude_re or config.field_selectors):
        return True

    try:
        data = json.loads(line)
        record = Record.from_line(data, config=config)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError):
        # Non-JSON lines don't match filters (but are printed as-is)
        return False

    if (_this_level := get_level(name=record.level)) == logging.NOTSET and record.level:
        record.data['_level_name'] = record.level

    # Use cached dotted keys for performance optimization
    for dotted_key in config.keys.get_dotted_keys():
        if value := dotted.get(record.data, dotted_key):
            record.data[dotted_key] = value if isinstance(value, str) else str(value)
            dotted.remove(record.data, dotted_key)

    # Format the record for filter checking
    printer_kwargs = {
        'message': record.message,
        'is_header': False,
        '_this_level': _this_level,
        '_is_text': False,
        '_console': console,
        '_styles': config.styles,
        '_keys_on_own_line': config.keys.on_own_line,
        'timestamp': record.timestamp,
    }
    keys = set(printer_kwargs)

    # Capture formatted output for filtering
    with console.capture() as capture:
        rich_printer(
            **printer_kwargs,  # type: ignore[arg-type]
            **{f' {key}' if key in keys else key: value for key, value in record.data.items()},
        )
    formatted_output = capture.get()

    # Check filters
    from tail_jsonl._private.filters import should_include_record

    return should_include_record(record, formatted_output.strip(), config)


def print_record(line: str, console: Console, config: Config, *, skip_filter: bool = False) -> bool:
    """Format and print the record.

    Args:
        line: Raw input line to process
        console: Rich console for output
        config: Configuration settings
        skip_filter: If True, print without applying filters (for context lines)

    Returns:
        True if line was printed (matched filters or skip_filter=True), False otherwise
    """
    try:
        data = json.loads(line)
        record = Record.from_line(data, config=config)
        if config.debug:
            console.print(
                (
                    f'[dim]DEBUG: Parsed keys - timestamp={record.timestamp!r},'
                    f' level={record.level!r}, message={record.message!r}[/dim]'
                ),
                markup=True,
                highlight=False,
            )
    except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError) as exc:
        if config.debug:
            console.print(
                f'[dim red]DEBUG: Failed to parse line as JSON: {exc.__class__.__name__}: {exc}[/dim red]',
                markup=True,
                highlight=False,
            )
        console.print(line.rstrip(), markup=False, highlight=False)  # Print the unmodified line
        return True  # Non-JSON lines are always printed

    if (_this_level := get_level(name=record.level)) == logging.NOTSET and record.level:
        record.data['_level_name'] = record.level

    # PLANNED: Consider moving to Corallium
    # Use cached dotted keys for performance optimization
    for dotted_key in config.keys.get_dotted_keys():
        if value := dotted.get(record.data, dotted_key):
            if config.debug:
                console.print(
                    f'[dim]DEBUG: Promoting dotted key {dotted_key!r} to own line[/dim]',
                    markup=True,
                    highlight=False,
                )
            record.data[dotted_key] = value if isinstance(value, str) else str(value)
            dotted.remove(record.data, dotted_key)

    # Format the record (capture output for filtering)
    printer_kwargs = {
        'message': record.message,
        'is_header': False,
        '_this_level': _this_level,
        '_is_text': False,
        '_console': console,
        '_styles': config.styles,
        '_keys_on_own_line': config.keys.on_own_line,
        'timestamp': record.timestamp,
    }
    keys = set(printer_kwargs)

    # Capture formatted output for filtering (Phase 3)
    with console.capture() as capture:
        rich_printer(
            **printer_kwargs,  # type: ignore[arg-type]
            # Try to print all values and avoid name collision
            **{f' {key}' if key in keys else key: value for key, value in record.data.items()},
        )
    formatted_output = capture.get()

    # Apply filters (Phase 3) - unless skip_filter is True (for context lines)
    if not skip_filter:
        from tail_jsonl._private.filters import should_include_record

        if not should_include_record(record, formatted_output.strip(), config):
            return False

    # Print the record if it passes all filters (preserve original formatting)
    console.print(formatted_output.rstrip('\n'), markup=False, highlight=False)
    return True
