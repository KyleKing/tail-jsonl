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

    @classmethod
    def from_dict(cls, data: dict) -> Keys:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(**data)


@dataclass
class Config:
    """`tail-jsonl` config."""

    styles: Styles = field(default_factory=Styles)
    keys: Keys = field(default_factory=Keys)

    @classmethod
    def from_dict(cls, data: dict) -> Config:  # type: ignore[type-arg]
        """Return Self instance."""
        return cls(
            styles=styles_from_dict(data.get('styles', {})),
            keys=Keys.from_dict(data.get('keys', {})),
        )
