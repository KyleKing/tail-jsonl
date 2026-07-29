"""Removal of keys that should never reach the renderer."""

from __future__ import annotations

from typing import Any

import dotted  # type: ignore[import-untyped]


def hide_keys(data: dict, patterns: list[Any]) -> None:  # type: ignore[type-arg]
    """Remove each parsed dotted key from the data in place. Absent keys are ignored."""
    for pattern in patterns:
        dotted.remove(data, pattern)
