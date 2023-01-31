"""Core print logic."""

import json
from copy import copy
from typing import Any

from beartype import beartype
from loguru import logger
from pydantic import BaseModel
from rich.console import Console
from rich.text import Text

from .config import Config


@beartype
def pop_key(data: dict, keys: list[str], fallback: str) -> Any:
    """Recursively pop whichever key matches first or default to the fallback."""
    try:
        key = keys.pop(0)
        return data.pop(key, None) or pop_key(data, keys, fallback)
    except IndexError:
        return fallback


class Record(BaseModel):
    """Record Model."""

    timestamp: str
    level: str
    message: str
    data: dict

    @classmethod
    def from_line(cls, data: dict, config: Config) -> 'Record':
        """Extract Record from jsonl."""
        return cls(
            timestamp=pop_key(data, copy(config.keys.timestamp), '<no timestamp>'),
            level=pop_key(data, copy(config.keys.level), '<no level>'),
            message=pop_key(data, copy(config.keys.message), '<no message>'),
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
