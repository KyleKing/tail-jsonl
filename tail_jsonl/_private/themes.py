"""Theme system for customizable color schemes (Phase 8)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from corallium.loggers.styles import Colors, Styles
from corallium.tomllib import tomllib


@dataclass
class Theme:
    """Color theme for log output."""

    name: str
    description: str

    # Level colors
    level_error: str = 'bold red'
    level_warning: str = 'yellow'
    level_info: str = 'blue'
    level_debug: str = 'dim white'
    level_notset: str = 'white'

    # Component colors
    timestamp: str = 'dim cyan'
    key: str = 'green'
    value: str = 'white'

    # Separators and borders
    separator: str = 'dim white'
    border: str = 'dim white'

    def to_styles(self) -> Styles:
        """Convert theme to Styles object for Rich console.

        Returns:
            Styles object compatible with corallium.loggers
        """
        colors = Colors(
            level_error=self.level_error,
            level_warn=self.level_warning,
            level_info=self.level_info,
            level_debug=self.level_debug,
            level_fallback=self.level_notset,
        )

        return Styles(
            colors=colors,
            # Additional style mappings can be added here
        )

    @classmethod
    def from_dict(cls, data: dict) -> Theme:  # type: ignore[type-arg]
        """Create Theme from dictionary."""
        return cls(**data)


# Built-in themes
BUILTIN_THEMES = {
    'dark': Theme(
        name='dark',
        description='Default dark theme (current behavior)',
        level_error='bold red',
        level_warning='yellow',
        level_info='blue',
        level_debug='dim white',
        level_notset='white',
        timestamp='dim cyan',
        key='green',
        value='white',
        separator='dim white',
        border='dim white',
    ),
    'none': Theme(
        name='none',
        description='No colors (monochrome)',
        level_error='white',
        level_warning='white',
        level_info='white',
        level_debug='white',
        level_notset='white',
        timestamp='white',
        key='white',
        value='white',
        separator='white',
        border='white',
    ),
    'catppuccin-light': Theme(
        name='catppuccin-light',
        description='Catppuccin Latte (light) theme',
        # Catppuccin Latte colors for light backgrounds
        level_error='bold #d20f39',  # Red
        level_warning='#df8e1d',  # Yellow
        level_info='#1e66f5',  # Blue
        level_debug='#9ca0b0',  # Surface2
        level_notset='#4c4f69',  # Text
        timestamp='dim #179299',  # Teal
        key='#40a02b',  # Green
        value='#4c4f69',  # Text
        separator='dim #9ca0b0',  # Surface2
        border='dim #9ca0b0',  # Surface2
    ),
}


def load_theme(theme_name: str | None = None, theme_path: Path | None = None) -> Theme:
    """Load theme by name or from file.

    Args:
        theme_name: Name of built-in theme
        theme_path: Path to custom theme TOML file

    Returns:
        Theme instance

    Raises:
        ValueError: If theme_name is not found
        FileNotFoundError: If theme_path doesn't exist
    """
    if theme_path:
        # Load custom theme from TOML file
        if not theme_path.exists():
            raise FileNotFoundError(f'Theme file not found: {theme_path}')

        data = tomllib.loads(theme_path.read_text(encoding='utf-8'))
        if 'theme' not in data:
            raise ValueError('Theme file must contain [theme] section')

        return Theme.from_dict(data['theme'])

    if theme_name:
        if theme_name in BUILTIN_THEMES:
            return BUILTIN_THEMES[theme_name]
        raise ValueError(f'Unknown theme: {theme_name}. Available: {", ".join(BUILTIN_THEMES.keys())}')

    return BUILTIN_THEMES['dark']  # Default theme


def list_themes() -> dict[str, str]:
    """Get dictionary of available themes with descriptions.

    Returns:
        Dictionary mapping theme names to descriptions
    """
    return {name: theme.description for name, theme in BUILTIN_THEMES.items()}
