"""Core print logic."""

import json
from copy import copy

import dotted
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional
from corallium.loggers.rich_printer import rich_printer
from corallium.loggers.styles import get_level
from pydantic import BaseModel
from rich.console import Console

from ..config import Config


@beartype
def _dot_pop(data: Dict, key: str) -> Optional[str]:  # type: ignore[type-arg]
    value = dotted.get(data, key)
    if isinstance(value, str):
        dotted.remove(data, key)
        return value
    return None


@beartype
def _pop_key(data: Dict, keys: List[str], fallback: str) -> Any:  # type: ignore[type-arg]
    """Recursively pop each key while searching for a match."""
    try:
        key = keys.pop(0)
    except IndexError:
        return fallback
    else:
        return _dot_pop(data, key) or _pop_key(data, keys, fallback)


@beartype
def pop_key(data: Dict, keys: List[str], fallback: str) -> Any:  # type: ignore[type-arg]
    """Safely find the first key in the data or default to the fallback."""
    return _pop_key(data, copy(keys), fallback)


class Record(BaseModel):
    """Record Model."""

    timestamp: str
    level: str
    message: str
    data: Dict  # type: ignore[type-arg]

    @classmethod
    @beartype
    def from_line(cls, data: Dict, config: Config) -> 'Record':  # type: ignore[type-arg]
        """Extract Record from jsonl."""
        return cls(
            timestamp=pop_key(data, config.keys.timestamp, '<no timestamp>'),
            level=pop_key(data, config.keys.level, ''),
            message=pop_key(data, config.keys.message, '<no message>'),
            data=data,
        )


@beartype
def print_record(line: str, console: Console, config: Config) -> None:
    """Format and print the record."""
    try:
        record = Record.from_line(json.loads(line), config=config)
    except Exception:  # noqa: PIE786
        console.print(line)  # Print the unmodified line
        return

    logline = record.dict()
    rich_printer(  # noqa: CAC001
        message=logline.pop('message'),
        is_header=False,
        _this_level=get_level(name=logline['level']),
        _is_text=False,
        _console=console,
        **logline,
    )
