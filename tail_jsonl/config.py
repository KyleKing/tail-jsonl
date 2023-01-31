"""Configuration."""

from functools import cached_property
from typing import Dict, List

from beartype import beartype
from pydantic import BaseModel, Field


class Styles(BaseModel):
    """Styles configuration.

    Refer to https://rich.readthedocs.io/en/latest/style.html for available style

    Inspired by: https://github.com/Delgan/loguru/blob/07f94f3c8373733119f85aa8b9ca05ace3325a4b/loguru/_defaults.py#L31-L73

    And: https://github.com/hynek/structlog/blob/bcfc7f9e60640c150bffbdaeed6328e582f93d1e/src/structlog/dev.py#L126-L141

    """

    timestamp: str = 'dim grey'
    message: str = ''

    level_error: str = 'bold red'
    level_warn: str = 'bold yellow'
    level_info: str = 'bold green'
    level_debug: str = 'bold blue'
    level_fallback: str = ''

    key: str = 'green'
    value: str = ''

    @cached_property
    def _level_lookup(self) -> Dict[str, str]:
        return {
            'ERROR': self.level_error,
            'WARNING': self.level_warn,
            'WARN': self.level_warn,
            'INFO': self.level_info,
            'DEBUG': self.level_debug,
        }

    @beartype
    def get_level_style(self, level: str) -> str:
        """Return the right style for the specified level."""
        return self._level_lookup.get(level.upper(), self.level_fallback)


class Keys(BaseModel):
    """Special Keys."""

    timestamp: List[str] = Field(default_factory=lambda: ['timestamp', 'record.time.repr'])
    level: List[str] = Field(default_factory=lambda: ['level', 'record.level.name'])
    message: List[str] = Field(default_factory=lambda: ['event', 'record.message'])

    on_own_line: List[str] = Field(default_factory=lambda: ['text', 'exception'])


class Config(BaseModel):
    """`tail-jsonl` config."""

    styles: Styles = Field(default_factory=Styles)
    keys: Keys = Field(default_factory=Keys)
