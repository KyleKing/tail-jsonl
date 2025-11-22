"""Highlighting logic for log output (Phase 4 - Stern-Aligned)."""

from __future__ import annotations

from rich.style import Style
from rich.text import Text

from tail_jsonl.config import Config

# Color palette for multiple highlight patterns
# Using background colors for visibility
HIGHLIGHT_COLORS = [
    'yellow',
    'cyan',
    'magenta',
    'green',
    'blue',
    'red',
]


def apply_highlighting(
    text: str,
    config: Config,
) -> Text | str:
    """Apply regex highlighting to text using Rich.

    Highlights all occurrences of patterns in the text with different background colors.
    Each pattern gets a unique color from the color palette (cycling if more patterns
    than colors).

    Args:
        text: Formatted output string to highlight
        config: Configuration with compiled highlight patterns

    Returns:
        Rich Text object with highlighting if patterns exist, or original string if no highlights
    """
    if not config._highlight_res:
        return text

    # Create Rich Text object from plain text
    rich_text = Text(text)

    # Apply each highlight pattern with a different color
    for i, pattern in enumerate(config._highlight_res):
        # Cycle through colors if more patterns than colors
        color = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
        # Use background color with black text for visibility
        style = Style(bgcolor=color, color='black', bold=True)

        # Find all matches in the text
        for match in pattern.finditer(text):
            start, end = match.span()
            # Apply style to the matched region
            # Rich handles overlapping styles automatically
            rich_text.stylize(style, start, end)

    return rich_text
