# Themes Directory

This directory contains example theme files for tail-jsonl.

## Built-in Themes

tail-jsonl includes the following built-in themes:

- **dark** - Default dark terminal theme (current behavior)
- **none** - No colors, monochrome output
- **catppuccin-light** - Catppuccin Latte theme for light backgrounds

## Custom Themes

You can create custom themes by creating a TOML file with the following structure:

```toml
[theme]
name = "my-theme"
description = "My custom theme"

# Level colors
level_error = "bold red"
level_warning = "yellow"
level_info = "blue"
level_debug = "dim white"
level_notset = "white"

# Component colors
timestamp = "dim cyan"
key = "green"
value = "white"

# Separators and borders
separator = "dim white"
border = "dim white"
```

## Usage

```bash
# Use built-in theme
tail-jsonl --theme dark < logs.jsonl
tail-jsonl --theme none < logs.jsonl
tail-jsonl --theme catppuccin-light < logs.jsonl

# Use custom theme
tail-jsonl --theme-path ~/.config/tail-jsonl/my-theme.toml < logs.jsonl

# List available themes
tail-jsonl --list-themes
```

## Color Format

Colors can be specified in several formats:

- **Named colors:** `red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `white`, `black`
- **Hex colors:** `#ff0000`, `#00ff00`, `#0000ff`
- **RGB:** `rgb(255,0,0)`
- **Modifiers:** `bold`, `dim`, `italic`, `underline`
- **Combined:** `bold red`, `dim #00ff00`, `italic blue`

See `example-custom.toml` for a complete example.
