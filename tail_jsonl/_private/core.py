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


def print_record(line: str, console: Console, config: Config) -> None:
    """Format and print the record."""
    try:
        data = json.loads(line)
        record = Record.from_line(data, config=config)
        if config.debug:
            console.print(
                f'[dim]DEBUG: Parsed keys - timestamp={record.timestamp!r}, '
                f'level={record.level!r}, message={record.message!r}[/dim]',
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

    if (_this_level := get_level(name=record.level)) == logging.NOTSET and record.level:
        record.data['_level_name'] = record.level

    # PLANNED: Consider moving to Corallium
    for dotted_key in config.keys.on_own_line:
        if '.' not in dotted_key:
            continue
        if value := dotted.get(record.data, dotted_key):
            if config.debug:
                console.print(
                    f'[dim]DEBUG: Promoting dotted key {dotted_key!r} to own line[/dim]', markup=True, highlight=False,
                )
            record.data[dotted_key] = value if isinstance(value, str) else str(value)
            dotted.remove(record.data, dotted_key)

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
    rich_printer(
        **printer_kwargs,  # type: ignore[arg-type]
        # Try to print all values and avoid name collision
        **{f' {key}' if key in keys else key: value for key, value in record.data.items()},
    )
