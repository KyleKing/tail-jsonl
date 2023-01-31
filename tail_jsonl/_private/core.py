"""Core print logic."""

import json
from copy import copy
from typing import Any, Dict, List, Optional

import dotted
from beartype import beartype
from loguru import logger
from pydantic import BaseModel
from rich.console import Console
from rich.text import Text

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
        return _dot_pop(data, key) or _pop_key(data, keys, fallback)
    except IndexError:
        return fallback


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
    def from_line(cls, data: Dict, config: Config) -> 'Record':  # type: ignore[type-arg]
        """Extract Record from jsonl."""
        return cls(
            timestamp=pop_key(data, config.keys.timestamp, '<no timestamp>'),
            level=pop_key(data, config.keys.level, '<no level>'),
            message=pop_key(data, config.keys.message, '<no message>'),
            data=data,
        )


@beartype
def print_record(line: str, console: Console, config: Config) -> None:
    """Format and print the record."""
    try:
        record = Record.from_line(json.loads(line), config=config)
    except Exception:
        logger.exception('Error in tail-json to parse line', line=line)
        console.print('')  # Line break
        return

    text = Text(tab_size=4)  # FIXME: Why isn't this indenting what is wrapped?
    text.append(f'{record.timestamp: <28}', style=config.styles.timestamp)
    text.append(f' {record.level: <7}', style=config.styles.get_level_style(record.level))
    text.append(f' {record.message: <20}', style=config.styles.message)

    full_lines = []
    for key in config.keys.on_own_line:
        line = record.data.pop(key, None)
        if line:
            full_lines.append((key, line))

    for key, value in record.data.items():
        text.append(f' {key}:', style=config.styles.key)
        text.append(f' {str(value): <10}', style=config.styles.value)

    console.print(text)
    for key, line in full_lines:
        new_text = Text()
        new_text.append(f' ∟ {key}', style='bold green')
        new_text.append(f': {line}')
        console.print(new_text)
