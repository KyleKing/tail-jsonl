"""Core print logic."""

from __future__ import annotations

import json
import logging
from copy import copy
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


def _pop_key(data: dict, keys: list[str], fallback: str) -> Any:  # type: ignore[type-arg]
    """Return result of recursively popping each key while searching for a match."""
    try:
        key = keys.pop(0)
    except IndexError:
        return fallback
    return _dot_pop(data, key) or _pop_key(data, keys, fallback)


def pop_key(data: dict, keys: list[str], fallback: str) -> Any:  # type: ignore[type-arg]
    """Return the first key in the data or default to the fallback."""
    return _pop_key(data, copy(keys), fallback)


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
        record = Record.from_line(json.loads(line), config=config)
    except Exception:
        console.print(line.rstrip(), markup=False, highlight=False)  # Print the unmodified line
        return

    if (_this_level := get_level(name=record.level)) == logging.NOTSET and record.level:
        record.data['_level_name'] = record.level

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
        # Ensure that there is no repeat keyword arguments
        **{f'_{key}' if key in keys else key: value for key, value in record.data.items()},
    )
