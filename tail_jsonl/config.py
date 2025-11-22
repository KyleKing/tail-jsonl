"""Configuration."""

from __future__ import annotations

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

    @classmethod
    def from_dict(cls, data: dict) -> Config:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(
            styles=styles_from_dict(data.get('styles', {})),
            keys=Keys.from_dict(data.get('keys', {})),
            debug=data.get('debug', False),
        )
