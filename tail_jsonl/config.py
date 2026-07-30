"""Configuration."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import dotted  # type: ignore[import-untyped]
from corallium.loggers.styles import LEVELS, Styles, get_level
from dotted.api import ParseError  # type: ignore[import-untyped]

from tail_jsonl._private.timestamps import resolve_zone

LEVEL_NAMES = tuple(sorted(name.lower() for name in LEVELS))
"""Level names accepted by `min_level`, shared with the renderer so the two agree."""


def _parse_min_level(name: str) -> int:
    if (level := get_level(name=name)) == logging.NOTSET:
        expected = ', '.join(LEVEL_NAMES)
        msg = f'Unrecognized level {name!r}. Expected one of: {expected}'
        raise ValueError(msg)
    return level


def _parse_dotted_key(key: str) -> Any:
    try:
        return dotted.parse(key)
    except ParseError as err:
        msg = f'Unparseable dotted key {key!r}: {err}'
        raise ValueError(msg) from err


def _parse_selector(selector: str) -> tuple[str, str]:
    key, separator, pattern = selector.partition('=')
    if not separator or not key:
        msg = f'Field selectors must be formatted as KEY=PATTERN, but received {selector!r}'
        raise ValueError(msg)
    return (key, pattern)


@dataclass
class Keys:
    """Special Keys."""

    # TODO: Are these dotted keys properly parsed?
    timestamp: list[str] = field(default_factory=lambda: ['timestamp', 'time', 'record.time.repr'])
    level: list[str] = field(default_factory=lambda: ['level', 'levelname', 'record.level.name'])
    message: list[str] = field(default_factory=lambda: ['event', 'message', 'msg', 'record.message'])

    on_own_line: list[str] = field(default_factory=lambda: ['text', 'exception', 'error.stack'])

    @classmethod
    def from_dict(cls, data: dict) -> Keys:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(**data)


@dataclass
class Filters:
    """Line and record filters.

    Patterns are compiled on creation, so replace the instance rather than mutating an attribute.
    """

    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    field_selectors: list[str] = field(default_factory=list)
    case_insensitive: bool = False
    min_level: str | None = None

    include_patterns: list[re.Pattern[str]] = field(init=False, repr=False, default_factory=list)
    exclude_patterns: list[re.Pattern[str]] = field(init=False, repr=False, default_factory=list)
    selector_patterns: list[tuple[str, re.Pattern[str]]] = field(init=False, repr=False, default_factory=list)
    min_level_value: int = field(init=False, repr=False, default=logging.NOTSET)
    filters_line: bool = field(init=False, repr=False, default=False)
    filters_record: bool = field(init=False, repr=False, default=False)

    def __post_init__(self) -> None:
        """Compile the patterns and precompute whether any filter is active."""
        flags = re.IGNORECASE if self.case_insensitive else 0
        self.include_patterns = [re.compile(_, flags) for _ in self.include]
        self.exclude_patterns = [re.compile(_, flags) for _ in self.exclude]
        self.selector_patterns = [
            (key, re.compile(pattern, flags)) for key, pattern in map(_parse_selector, self.field_selectors)
        ]
        self.min_level_value = _parse_min_level(self.min_level) if self.min_level else logging.NOTSET
        self.filters_line = bool(self.include_patterns or self.exclude_patterns)
        self.filters_record = bool(self.selector_patterns or self.min_level_value)

    @classmethod
    def from_dict(cls, data: dict) -> Filters:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(**data)


@dataclass
class Render:
    """Timestamp and key rendering options.

    Hidden keys are parsed on creation, so replace the instance rather than mutating an attribute.
    """

    time_zone: str | None = None
    time_format: str | None = None
    hidden_keys: list[str] = field(default_factory=list)

    hidden_patterns: list[tuple[Any, str]] = field(init=False, repr=False, default_factory=list)
    hides_keys: bool = field(init=False, repr=False, default=False)

    def __post_init__(self) -> None:
        """Parse the dotted keys and reject an unknown zone before the first line is read."""
        self.hidden_patterns = [(_parse_dotted_key(_), _) for _ in self.hidden_keys]
        self.hides_keys = bool(self.hidden_patterns)
        if self.time_zone:
            resolve_zone(self.time_zone)

    @classmethod
    def from_dict(cls, data: dict) -> Render:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(**data)


@dataclass
class Config:
    """`tail-jsonl` config."""

    styles: Styles = field(default_factory=Styles)
    keys: Keys = field(default_factory=Keys)
    filters: Filters = field(default_factory=Filters)
    render: Render = field(default_factory=Render)
    debug: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> Config:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(
            styles=Styles.from_dict(data.get('styles', {})),
            keys=Keys.from_dict(data.get('keys', {})),
            filters=Filters.from_dict(data.get('filters', {})),
            render=Render.from_dict(data.get('render', {})),
            debug=data.get('debug', False),
        )
