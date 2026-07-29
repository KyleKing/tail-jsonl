"""Core print logic."""

from __future__ import annotations

import json
import logging
from typing import Any

import dotted  # type: ignore[import-untyped]
from corallium.loggers.rich_printer import rich_printer
from corallium.loggers.styles import get_level
from rich.console import Console

from tail_jsonl._private.filters import line_passes, record_passes
from tail_jsonl._private.types import Record
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


def _promote_dotted_keys(
    *,
    data: dict,  # type: ignore[type-arg]
    dotted_keys: list[str],
    console: Console,
    debug: bool,
) -> None:
    """Promote dotted keys to top-level for proper formatting on own line.

    Dotted key promotion is application-specific to tail-jsonl's formatting needs
    and requires the external 'dotted' library, so it remains here rather than
    being moved to the general-purpose Corallium library.
    """
    for dotted_key in dotted_keys:
        if '.' not in dotted_key:
            continue
        if value := dotted.get(data, dotted_key):
            if debug:
                console.print(
                    f'[dim]DEBUG: Promoting dotted key {dotted_key!r} to own line[/dim]',
                    markup=True,
                    highlight=False,
                )
            data[dotted_key] = value if isinstance(value, str) else str(value)
            dotted.remove(data, dotted_key)


def record_from_line(data: dict, config: Config) -> Record:  # type: ignore[type-arg]
    """Return Record from jsonl."""
    return Record(
        timestamp=pop_key(data, config.keys.timestamp, '<no timestamp>'),
        level=pop_key(data, config.keys.level, ''),
        message=pop_key(data, config.keys.message, '<no message>'),
        data=data,
    )


def print_record(line: str, console: Console, config: Config) -> None:
    """Format and print the record.

    Lines that cannot be parsed as JSON are printed verbatim, so only the raw include and exclude
    patterns can drop them.
    """
    filters = config.filters
    if filters.filters_line and not line_passes(line, filters):
        return
    try:
        data = json.loads(line)
        record = record_from_line(data, config=config)
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
        return

    if filters.filters_record and not record_passes(record, filters):
        return

    if (this_level := get_level(name=record.level)) == logging.NOTSET and record.level:
        record.data['_level_name'] = record.level

    _promote_dotted_keys(
        data=record.data,
        dotted_keys=config.keys.on_own_line,
        console=console,
        debug=config.debug,
    )

    printer_kwargs = {
        'message': record.message,
        'is_header': False,
        '_this_level': this_level,
        '_is_text': False,
        '_console': console,
        '_styles': config.styles,
        '_keys_on_own_line': config.keys.on_own_line,
        'timestamp': record.timestamp,
    }
    keys = set(printer_kwargs)
    rich_printer(
        **printer_kwargs,  # type: ignore[arg-type]
        # Try to print all values and avoid name collision
        **{f' {key}' if key in keys else key: value for key, value in record.data.items()},
    )
