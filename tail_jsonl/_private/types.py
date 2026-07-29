"""Type definitions for tail-jsonl."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Record:
    """Record Model."""

    timestamp: str
    level: str
    message: str
    data: dict  # type: ignore[type-arg]
