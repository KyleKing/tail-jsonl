"""Removal of keys that should never reach the renderer."""

from __future__ import annotations

from typing import Any

import dotted  # type: ignore[import-untyped]


def remove_key(data: dict, pattern: Any, key: str) -> None:  # type: ignore[type-arg]
    """Remove a dotted key in place, along with any container it leaves empty.

    `pattern` is the parsed form of `key`, so callers can reuse a pattern parsed once.
    """
    dotted.remove(data, pattern)
    prune_empty_parents(data, key)


def prune_empty_parents(data: dict, key: str) -> None:  # type: ignore[type-arg]
    """Drop the containers along a dotted key that no longer hold anything.

    Pruning is scoped to the ancestors of `key`, so an unrelated mapping logged as `{}` survives.
    """
    parents = key.split('.')[:-1]
    while parents:
        parent = dotted.get(data, '.'.join(parents))
        if not isinstance(parent, dict) or parent:
            return
        dotted.remove(data, '.'.join(parents))
        parents.pop()


def hide_keys(data: dict, patterns: list[tuple[Any, str]]) -> None:  # type: ignore[type-arg]
    """Remove each parsed dotted key from the data in place. Absent keys are ignored."""
    for pattern, key in patterns:
        remove_key(data, pattern, key)
