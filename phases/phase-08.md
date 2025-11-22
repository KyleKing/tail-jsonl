# Phase 8: Themes & Shell Completions ⚠️ REVIEW REQUIRED

**Priority:** LOW
**External Dependencies:** Depends on approach chosen for shell completions
**Estimated Complexity:** Medium
**Status:** 🔍 **REVIEWED**

## ⚠️ Review Questions

Before implementing this phase, please review and decide:

### Theme/Colorization Questions

1. **Theme storage format:**
   - **Option A:** Hardcoded Python dictionaries
     - ✅ No file I/O, fast
     - ✅ Type-safe
     - ❌ Requires code changes to add themes

   - [x] **Option B:** TOML files in package (extend the existing pattern for configuration)
     - ✅ Easy to add new themes
     - ✅ Users can create custom themes
     - ❌ File I/O overhead

   - **Option C:** Mix (built-in themes + custom path)
     - ✅ Best of both
     - ✅ Extensible
     - ❌ More complex

2. **Which themes to include initially?**
   - [x] Dark (current default)
   - Light
   - [x] Solarized Dark/Light
   - [x] Catppuccin Dark/Light (popular)
   - Dracula
   - Nord
   - Minimal (reduced colors)
   - [x] None (no colors)

3. **Theme components:**
   - What should be themeable? (
     - Level colors (ERROR=red, INFO=blue, etc.)
     - Key colors
     - Value colors
     - Timestamp color
     - Border/separator colors
   - [x] Don't go crazy and only marginally extend the functionality offered today unless critical to the feature to extend

### Shell Completion Questions

1. **Completion library choice:**
   - [x] **Option A:** Use invoke's built-in completions
     - ✅ No extra dependency
     - ✅ Simple integration
     - ❌ Limited documentation
     - ❌ May not support all shells (only bash and zsh support is required)

   - **Option B:** Use `usage` (GitHub: jdx/usage) (fall back to `usage` if blocked on invoke)
     - ✅ Modern, well-maintained
     - ✅ Good shell support
     - ✅ Easy configuration
     - ❌ Rust binary dependency
     - ❌ External tool required

   - **Option C:** Use `argcomplete`
     - ✅ Pure Python
     - ✅ Good bash/zsh support
     - ❌ Doesn't work with invoke tasks directly
     - ❌ Requires click or argparse (we use invoke)

   - **Option D:** Use `shtab`
     - ✅ Supports click, argparse
     - ❌ Doesn't integrate with invoke well

   - **Option E:** Manual shell scripts
     - ✅ Full control
     - ✅ No dependencies
     - ❌ Maintenance burden
     - ❌ Hard to keep in sync with CLI changes

2. **Supported shells:**
   - [x] bash (most common)
   - [x] zsh (macOS default, popular)
   - fish (growing popularity) (optional)
   - PowerShell (Windows) (optional)

3. **Installation approach:**
   - Generate completion script to stdout?
   - Auto-install to shell rc files?
   - Provide installer command?
   - Do what makes sense. Typically I have seen a CLI argument `--completions` like for stern (https://github.com/stern/stern#cli-flags)

**Recommended Approach (Subject to Review):**
- **Themes:** Option C (built-in + custom path)
- **Completions:** Try Option A (invoke built-in) first, fallback to Option B (usage) if insufficient
- **Shells:** bash and zsh as minimum, fish if easy

## Objectives

Improve user experience with customizable color themes and shell completions for faster command-line usage.

## Features

### 4.8 Colorization Presets (Themes)

**Goal:** Named color schemes for different terminal environments and preferences

**Example Usage:**

```bash
# List available themes
tail-jsonl --list-themes

# Use a theme
tail-jsonl --theme=light
tail-jsonl --theme=solarized-dark
tail-jsonl --theme=catppuccin
tail-jsonl --theme=none  # Disable all colors

# Custom theme from file
tail-jsonl --theme-path=~/.config/tail-jsonl/my-theme.toml

# Override with --config-path (existing behavior)
tail-jsonl --config-path=~/.tail-jsonl.toml
```

**Implementation Plan:**

1. **Define theme schema:**
   ```python
   # tail_jsonl/_private/themes.py
   from dataclasses import dataclass
   from typing import Dict

   @dataclass
   class Theme:
       """Color theme for log output."""
       name: str
       description: str

       # Level colors
       level_error: str = "bold red"
       level_warning: str = "yellow"
       level_info: str = "blue"
       level_debug: str = "dim white"

       # Component colors
       timestamp: str = "dim cyan"
       key: str = "green"
       value: str = "white"
       string_value: str = "yellow"
       number_value: str = "cyan"
       bool_value: str = "magenta"
       null_value: str = "dim white"

       # Separators
       separator: str = "dim white"
       border: str = "dim white"

       def to_dict(self) -> Dict[str, str]:
           """Convert to dictionary for Rich styling."""
           return {
               'level.error': self.level_error,
               'level.warning': self.level_warning,
               'level.info': self.level_info,
               'level.debug': self.level_debug,
               'timestamp': self.timestamp,
               'key': self.key,
               'value': self.value,
               'string': self.string_value,
               'number': self.number_value,
               'bool': self.bool_value,
               'null': self.null_value,
               'separator': self.separator,
               'border': self.border,
           }
   ```

2. **Create built-in themes:**
   ```python
   THEMES = {
       'dark': Theme(
           name='dark',
           description='Default dark theme (current behavior)',
           # ... color definitions ...
       ),
       'light': Theme(
           name='light',
           description='Light terminal backgrounds',
           level_error="bold red",
           level_warning="yellow",
           level_info="blue",
           # ... adjusted for light backgrounds ...
       ),
       'solarized-dark': Theme(
           name='solarized-dark',
           description='Solarized Dark color scheme',
           # ... Solarized colors ...
       ),
       'none': Theme(
           name='none',
           description='No colors (monochrome)',
           level_error="white",
           level_warning="white",
           level_info="white",
           # All white/no styling
       ),
   }
   ```

3. **Add theme loading:**
   ```python
   def load_theme(theme_name: str = None, theme_path: Path = None) -> Theme:
       """Load theme by name or from file."""
       if theme_path:
           # Load custom theme from TOML
           import toml
           data = toml.load(theme_path)
           return Theme(**data['theme'])

       if theme_name:
           if theme_name in THEMES:
               return THEMES[theme_name]
           else:
               raise ValueError(f"Unknown theme: {theme_name}")

       return THEMES['dark']  # Default
   ```

4. **Add CLI flags:**
   ```python
   @invoke.task(
       help={
           'theme': 'Color theme name (dark, light, solarized-dark, none)',
           'theme-path': 'Path to custom theme TOML file',
           'list-themes': 'List available built-in themes and exit',
       }
   )
   def main(ctx, theme='dark', theme_path=None, list_themes=False, ...):
       if list_themes:
           console.print("[bold]Available themes:[/bold]\n")
           for name, theme in THEMES.items():
               console.print(f"  {name}: {theme.description}")
           sys.exit(0)
   ```

5. **Integrate with Rich console:**
   ```python
   def create_console(theme: Theme) -> Console:
       """Create Rich console with theme applied."""
       # Apply theme styles to console
       console = Console(theme=RichTheme(theme.to_dict()))
       return console
   ```

**Acceptance Criteria:**
- [ ] Review decisions on themes and storage format approved
- [ ] At least 3 built-in themes (dark, light, none)
- [ ] `--theme` flag selects theme
- [ ] `--theme-path` loads custom theme from file
- [ ] `--list-themes` shows available themes
- [ ] Custom theme file format documented
- [ ] Themes integrate with Rich console
- [ ] Tests for theme loading and application
- [ ] Documentation with theme examples

### 4.12 Shell Completions

**Goal:** Generate shell completions for faster command-line usage

**Example Usage:**

```bash
# Generate completion script for bash
tail-jsonl --completion bash

# Generate for zsh
tail-jsonl --completion zsh

# Install completions (if supported)
tail-jsonl --install-completion
```

**Example Completions:**

```bash
# User types:
tail-jsonl --the<TAB>

# Shell completes to:
tail-jsonl --theme=

# User types:
tail-jsonl --theme=<TAB>

# Shell shows:
dark  light  solarized-dark  none
```

**Implementation Plan (Option A - invoke built-in):**

1. **Check invoke completion support:**
   ```python
   # Research invoke completion capabilities
   # Document findings on what's supported
   ```

2. **If supported, implement completion generation:**
   ```python
   @invoke.task
   def completion(ctx, shell='bash'):
       """Generate shell completion script."""
       # Use invoke's built-in completion if available
       # Generate script to stdout
       pass
   ```

**Implementation Plan (Option B - usage tool):**

1. **Add usage spec file:**
   ```toml
   # .usage.toml or usage.kdl
   name = "tail-jsonl"
   bin = "tail-jsonl"
   about = "Format and view JSON logs"

   [[flag]]
   name = "theme"
   long = "theme"
   help = "Color theme name"
   arg = "THEME"
   choices = ["dark", "light", "solarized-dark", "none"]

   [[flag]]
   name = "level"
   long = "level"
   help = "Filter by log level"
   arg = "LEVEL"

   # ... more flags ...
   ```

2. **Add completion generation:**
   ```python
   @invoke.task
   def completion(ctx, shell='bash'):
       """Generate shell completion script using usage."""
       import subprocess
       result = subprocess.run(
           ['usage', 'generate', shell, '.usage.toml'],
           capture_output=True,
           text=True,
       )
       print(result.stdout)
   ```

**Implementation Plan (Option E - manual scripts):**

If other options don't work well:

1. **Create completion scripts manually:**
   ```bash
   # completions/tail-jsonl.bash
   _tail_jsonl_completions() {
       local cur prev opts
       COMPREPLY=()
       cur="${COMP_WORDS[COMP_CWORD]}"
       prev="${COMP_WORDS[COMP_CWORD-1]}"

       opts="--theme --level --filter --search --stats --help"

       case "${prev}" in
           --theme)
               COMPREPLY=( $(compgen -W "dark light solarized-dark none" -- ${cur}) )
               return 0
               ;;
           --level)
               COMPREPLY=( $(compgen -W "error warning info debug" -- ${cur}) )
               return 0
               ;;
           *)
               ;;
       esac

       COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
       return 0
   }
   complete -F _tail_jsonl_completions tail-jsonl
   ```

2. **Add installation instructions to docs:**
   ```markdown
   # Shell Completions

   ## Bash

   Add to ~/.bashrc:
   ```bash
   source <(tail-jsonl --completion bash)
   ```

   Or install permanently:
   ```bash
   tail-jsonl --completion bash > /etc/bash_completion.d/tail-jsonl
   ```
   ```

**Acceptance Criteria:**
- [ ] Review decision on completion approach approved
- [ ] Completions work for bash
- [ ] Completions work for zsh (if feasible)
- [ ] Complete flag names (--theme, --level, etc.)
- [ ] Complete flag values (theme names, etc.)
- [ ] Installation instructions documented
- [ ] Tests (if applicable)
- [ ] Documentation with setup examples

## Testing Strategy

**Theme Tests:**

1. **Theme loading tests:**
   ```python
   def test_load_builtin_theme():
       theme = load_theme('dark')
       assert theme.name == 'dark'
       assert theme.level_error == 'bold red'

   def test_load_custom_theme(tmp_path):
       theme_file = tmp_path / "custom.toml"
       theme_file.write_text("""
       [theme]
       name = "custom"
       description = "Custom theme"
       level_error = "magenta"
       """)
       theme = load_theme(theme_path=theme_file)
       assert theme.name == 'custom'
       assert theme.level_error == 'magenta'
   ```

2. **Theme application tests:**
   - Verify theme styles applied to console
   - Test each theme visually (manual)
   - Ensure 'none' theme has no colors

**Completion Tests:**

- Manual testing in actual shells
- Verify generated scripts are valid
- Test completion of flag names
- Test completion of flag values

## Performance Considerations

- Theme loading: One-time at startup, no impact
- Completions: Generated once, no runtime impact

## Deliverables

### Themes
- [ ] Review decisions approved
- [ ] Theme schema and class
- [ ] 3+ built-in themes
- [ ] Custom theme loading from file
- [ ] `--theme`, `--theme-path`, `--list-themes` flags
- [ ] Integration with Rich console
- [ ] Theme documentation and examples
- [ ] Tests for theme loading

### Shell Completions
- [ ] Review decision on approach approved
- [ ] Completion generation implementation
- [ ] Support for bash
- [ ] Support for zsh (if feasible)
- [ ] Installation documentation
- [ ] Example completion scripts
- [ ] Manual testing in shells

## Future Extensions (Not in Phase 8)

- Theme editor/creator tool
- Auto-detect terminal background (light/dark)
- Dynamic theme switching based on time of day
- More shells: fish, PowerShell
- Completion caching for performance

## Dependencies

### Themes
- Python `tomllib` (stdlib in Python 3.11+) or `toml` for custom themes
- Rich (existing dependency)

### Completions
- Depends on chosen approach:
  - Option A: invoke (existing)
  - Option B: `usage` tool (external binary)
  - Option E: None (manual scripts)

## Notes

⚠️ **STOP: Do not implement until review questions are answered.**

Key decisions needed:
1. Theme storage format and which themes to include
2. Shell completion approach (invoke, usage, or manual)
3. Which shells to support initially

Themes are relatively straightforward but need design decisions. Completions are trickier with invoke-based CLI and may require research/experimentation.

Consider starting with themes only and deferring completions if too complex.
