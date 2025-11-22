"""Tests for theme system (Phase 8)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tail_jsonl._private.themes import BUILTIN_THEMES, Theme, list_themes, load_theme


class TestTheme:
    """Test Theme dataclass and methods."""

    def test_theme_creation(self):
        """Test creating a theme with default values."""
        theme = Theme(
            name='test',
            description='Test theme',
        )

        assert theme.name == 'test'
        assert theme.description == 'Test theme'
        assert theme.level_error == 'bold red'
        assert theme.level_warning == 'yellow'
        assert theme.level_info == 'blue'

    def test_theme_custom_colors(self):
        """Test creating a theme with custom colors."""
        theme = Theme(
            name='custom',
            description='Custom theme',
            level_error='magenta',
            level_warning='cyan',
            timestamp='#ff0000',
        )

        assert theme.level_error == 'magenta'
        assert theme.level_warning == 'cyan'
        assert theme.timestamp == '#ff0000'

    def test_theme_to_styles(self):
        """Test converting theme to Styles object."""
        theme = Theme(
            name='test',
            description='Test theme',
            level_error='bold red',
            level_warning='yellow',
        )

        styles = theme.to_styles()

        assert styles.colors.level_error == 'bold red'
        assert styles.colors.level_warn == 'yellow'

    def test_theme_from_dict(self):
        """Test creating theme from dictionary."""
        data = {
            'name': 'dict-theme',
            'description': 'Theme from dict',
            'level_error': 'red',
            'level_info': 'blue',
        }

        theme = Theme.from_dict(data)

        assert theme.name == 'dict-theme'
        assert theme.description == 'Theme from dict'
        assert theme.level_error == 'red'
        assert theme.level_info == 'blue'


class TestBuiltinThemes:
    """Test built-in themes."""

    def test_dark_theme_exists(self):
        """Test that dark theme is defined."""
        assert 'dark' in BUILTIN_THEMES
        dark = BUILTIN_THEMES['dark']
        assert dark.name == 'dark'
        assert 'dark' in dark.description.lower()

    def test_none_theme_exists(self):
        """Test that none theme is defined."""
        assert 'none' in BUILTIN_THEMES
        none = BUILTIN_THEMES['none']
        assert none.name == 'none'
        assert none.level_error == 'white'
        assert none.level_warning == 'white'

    def test_catppuccin_light_theme_exists(self):
        """Test that catppuccin-light theme is defined."""
        assert 'catppuccin-light' in BUILTIN_THEMES
        catppuccin = BUILTIN_THEMES['catppuccin-light']
        assert catppuccin.name == 'catppuccin-light'
        assert 'catppuccin' in catppuccin.description.lower() or 'latte' in catppuccin.description.lower()

    def test_all_themes_have_required_fields(self):
        """Test that all built-in themes have required fields."""
        for name, theme in BUILTIN_THEMES.items():
            assert theme.name == name
            assert theme.description
            assert theme.level_error
            assert theme.level_warning
            assert theme.level_info
            assert theme.level_debug
            assert theme.level_notset
            assert theme.timestamp
            assert theme.key
            assert theme.value


class TestLoadTheme:
    """Test theme loading functions."""

    def test_load_default_theme(self):
        """Test loading default theme (dark)."""
        theme = load_theme()
        assert theme.name == 'dark'

    def test_load_theme_by_name(self):
        """Test loading theme by name."""
        theme = load_theme(theme_name='none')
        assert theme.name == 'none'

        theme = load_theme(theme_name='catppuccin-light')
        assert theme.name == 'catppuccin-light'

    def test_load_theme_unknown_name(self):
        """Test loading unknown theme raises error."""
        with pytest.raises(ValueError, match='Unknown theme'):
            load_theme(theme_name='nonexistent')

    def test_load_theme_from_file(self, tmp_path: Path):
        """Test loading theme from TOML file."""
        theme_file = tmp_path / 'custom.toml'
        theme_file.write_text(
            '''
[theme]
name = "custom"
description = "Custom test theme"
level_error = "magenta"
level_warning = "cyan"
level_info = "green"
level_debug = "dim white"
level_notset = "white"
timestamp = "#ff0000"
key = "yellow"
value = "white"
separator = "dim white"
border = "dim white"
''',
        )

        theme = load_theme(theme_path=theme_file)

        assert theme.name == 'custom'
        assert theme.description == 'Custom test theme'
        assert theme.level_error == 'magenta'
        assert theme.timestamp == '#ff0000'

    def test_load_theme_from_nonexistent_file(self, tmp_path: Path):
        """Test loading from nonexistent file raises error."""
        theme_file = tmp_path / 'nonexistent.toml'

        with pytest.raises(FileNotFoundError, match='Theme file not found'):
            load_theme(theme_path=theme_file)

    def test_load_theme_from_invalid_file(self, tmp_path: Path):
        """Test loading from file without [theme] section."""
        theme_file = tmp_path / 'invalid.toml'
        theme_file.write_text(
            '''
[not_theme]
name = "invalid"
''',
        )

        with pytest.raises(ValueError, match='must contain .theme. section'):
            load_theme(theme_path=theme_file)

    def test_theme_path_overrides_name(self, tmp_path: Path):
        """Test that theme_path takes precedence over theme_name."""
        theme_file = tmp_path / 'custom.toml'
        theme_file.write_text(
            '''
[theme]
name = "file-theme"
description = "From file"
level_error = "magenta"
''',
        )

        # If both are provided, theme_path should win
        theme = load_theme(theme_name='dark', theme_path=theme_file)

        assert theme.name == 'file-theme'


class TestListThemes:
    """Test list_themes function."""

    def test_list_themes_returns_dict(self):
        """Test that list_themes returns a dictionary."""
        themes = list_themes()

        assert isinstance(themes, dict)
        assert len(themes) >= 3  # At least dark, none, catppuccin-light

    def test_list_themes_contains_required_themes(self):
        """Test that list_themes contains required themes."""
        themes = list_themes()

        assert 'dark' in themes
        assert 'none' in themes
        assert 'catppuccin-light' in themes

    def test_list_themes_values_are_descriptions(self):
        """Test that list_themes values are descriptions."""
        themes = list_themes()

        for name, description in themes.items():
            assert isinstance(description, str)
            assert len(description) > 0
