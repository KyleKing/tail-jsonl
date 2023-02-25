"""Configuration."""


from beartype.typing import List
from corallium.loggers.styles import Styles
from pydantic import BaseModel, Field


class Keys(BaseModel):
    """Special Keys."""

    timestamp: List[str] = Field(default_factory=lambda: ['timestamp', 'record.time.repr'])
    level: List[str] = Field(default_factory=lambda: ['level', 'record.level.name'])
    message: List[str] = Field(default_factory=lambda: ['event', 'message', 'record.message'])

    on_own_line: List[str] = Field(default_factory=lambda: ['text', 'exception'])


class Config(BaseModel):
    """`tail-jsonl` config."""

    styles: Styles = Field(default_factory=Styles)
    keys: Keys = Field(default_factory=Keys)
