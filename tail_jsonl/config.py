"""Configuration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from corallium.loggers.styles import Colors, Styles


# PLANNED: temporary backward compatibility until part of Corallium
def styles_from_dict(data: dict) -> Styles:  # type: ignore[type-arg]
    """Return Self instance."""
    if colors := (data.pop('colors', None) or None):
        colors = Colors(**colors)
    return Styles(**data, colors=colors)


@dataclass
class Keys:
    """Special Keys."""

    timestamp: list[str] = field(default_factory=lambda: ['timestamp', 'time', 'record.time.repr'])
    level: list[str] = field(default_factory=lambda: ['level', 'levelname', 'record.level.name'])
    message: list[str] = field(default_factory=lambda: ['event', 'message', 'msg', 'record.message'])

    on_own_line: list[str] = field(default_factory=lambda: ['text', 'exception', 'error.stack'])

    # Cache for dotted keys (keys that contain '.')
    _dotted_keys: list[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize cached dotted keys list."""
        # Pre-filter keys that contain '.' for performance optimization
        self._dotted_keys = [key for key in self.on_own_line if '.' in key]

    def get_dotted_keys(self) -> list[str]:
        """Return cached list of dotted keys from on_own_line.

        This is an optimization to avoid checking every key for '.' on every log line.
        """
        return self._dotted_keys

    @classmethod
    def from_dict(cls, data: dict) -> Keys:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(**data)


@dataclass
class Config:
    """`tail-jsonl` config."""

    styles: Styles = field(default_factory=Styles)
    keys: Keys = field(default_factory=Keys)
    debug: bool = False

    # Filtering options (Phase 3)
    include_pattern: str | None = None  # Regex allowlist
    exclude_pattern: str | None = None  # Regex blocklist
    field_selectors: list[tuple[str, str]] | None = None  # [(key, value_pattern), ...]
    case_insensitive: bool = False  # For regex matching

    # Timestamp formatting options (Phase 6)
    timestamp_format: str | None = None  # Format type: 'iso', 'relative', or custom format string
    timestamp_timezone: str | None = None  # Timezone for timestamp display

    # Compiled regex patterns (cached)
    _include_re: re.Pattern[str] | None = field(default=None, init=False, repr=False)
    _exclude_re: re.Pattern[str] | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Compile regex patterns for performance."""
        flags = re.IGNORECASE if self.case_insensitive else 0
        if self.include_pattern:
            self._include_re = re.compile(self.include_pattern, flags)
        if self.exclude_pattern:
            self._exclude_re = re.compile(self.exclude_pattern, flags)

    @classmethod
    def from_dict(cls, data: dict) -> Config:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(
            styles=styles_from_dict(data.get('styles', {})),
            keys=Keys.from_dict(data.get('keys', {})),
            debug=data.get('debug', False),
            include_pattern=data.get('include_pattern'),
            exclude_pattern=data.get('exclude_pattern'),
            field_selectors=data.get('field_selectors'),
            case_insensitive=data.get('case_insensitive', False),
            timestamp_format=data.get('timestamp_format'),
            timestamp_timezone=data.get('timestamp_timezone'),
        )
