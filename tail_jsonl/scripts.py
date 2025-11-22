"""Start the command line program."""

from __future__ import annotations

import argparse
import fileinput
import sys
from pathlib import Path

from corallium.tomllib import tomllib
from rich.console import Console

from . import __version__
from ._private.core import print_record
from .config import Config


def _load_config(
    config_path: str | None,
    *,
    debug: bool = False,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    field_selectors: list[tuple[str, str]] | None = None,
    case_insensitive: bool = False,
    highlight_patterns: list[str] | None = None,
    highlight_case_sensitive: bool = False,
    show_stats: bool = False,
    stats_only: bool = False,
    stats_json: bool = False,
) -> Config:
    """Return loaded specified configuration file with CLI overrides."""
    user_config: dict = {}  # type: ignore[type-arg]
    if config_path:
        pth = Path(config_path).expanduser()
        user_config = tomllib.loads(pth.read_text(encoding='utf-8'))
    config = Config.from_dict(user_config)

    # CLI flags override config file (Phase 3)
    if debug:
        config.debug = True
    if include_pattern is not None:
        config.include_pattern = include_pattern
        config.__post_init__()  # Recompile regex
    if exclude_pattern is not None:
        config.exclude_pattern = exclude_pattern
        config.__post_init__()  # Recompile regex
    if field_selectors is not None:
        config.field_selectors = field_selectors
    if case_insensitive:
        config.case_insensitive = case_insensitive
        config.__post_init__()  # Recompile regex with new flags

    # CLI flags for highlighting (Phase 4)
    if highlight_patterns is not None:
        config.highlight_patterns = highlight_patterns
        config.__post_init__()  # Recompile highlight patterns
    if highlight_case_sensitive:
        config.highlight_case_sensitive = highlight_case_sensitive
        config.__post_init__()  # Recompile with new flags

    # CLI flags for statistics (Phase 5)
    if show_stats:
        config.show_stats = show_stats
    if stats_only:
        config.stats_only = stats_only
        config.show_stats = True  # stats_only implies show_stats
    if stats_json:
        config.stats_json = stats_json

    return config


def start() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    parser = argparse.ArgumentParser(description='Pipe JSONL Logs for pretty printing')
    parser.add_argument(
        '-v', '--version', action='version',
        version=f'%(prog)s {__version__}', help="Show program's version number and exit.",
    )
    parser.add_argument('--config-path', help='Path to a configuration file')
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug mode to show parsing details and error information',
    )

    # Phase 3: Filtering flags (stern-aligned)
    parser.add_argument(
        '-i', '--include',
        dest='include_pattern',
        help='Include only lines matching regex pattern (allowlist, like stern -i)',
    )
    parser.add_argument(
        '-e', '--exclude',
        dest='exclude_pattern',
        help='Exclude lines matching regex pattern (blocklist, like stern -e)',
    )
    parser.add_argument(
        '--field-selector',
        action='append',
        dest='field_selectors',
        metavar='KEY=PATTERN',
        help=(
            'Filter by field key=value with glob support (like stern --field-selector). '
            'Can be repeated for AND logic. Example: --field-selector level=error'
        ),
    )
    parser.add_argument(
        '--case-insensitive',
        action='store_true',
        help='Case-insensitive regex matching for include/exclude patterns',
    )

    # Phase 4: Highlighting flags (stern-aligned)
    parser.add_argument(
        '-H', '--highlight',
        action='append',
        dest='highlight_patterns',
        metavar='PATTERN',
        help=(
            'Highlight regex pattern in output (like stern -H). '
            'Can be repeated for multiple patterns with different colors. '
            'Example: -H error -H warning'
        ),
    )
    parser.add_argument(
        '--highlight-case-sensitive',
        action='store_true',
        help='Case-sensitive highlighting (default: case-insensitive)',
    )

    # Phase 5: Statistics flags
    parser.add_argument(
        '--stats',
        action='store_true',
        dest='show_stats',
        help='Show statistics summary at end of processing',
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Only show statistics, suppress log output',
    )
    parser.add_argument(
        '--stats-json',
        action='store_true',
        help='Output statistics as JSON',
    )

    options = parser.parse_args(sys.argv[1:])
    sys.argv = sys.argv[:1]  # Remove CLI before calling fileinput

    # Parse field selectors from "key=value" format
    field_selectors = None
    if options.field_selectors:
        field_selectors = []
        for selector in options.field_selectors:
            if '=' not in selector:
                parser.error(f'Field selector must be in format KEY=PATTERN, got: {selector}')
            key, value = selector.split('=', 1)
            field_selectors.append((key, value))

    config = _load_config(
        options.config_path,
        debug=options.debug,
        include_pattern=options.include_pattern,
        exclude_pattern=options.exclude_pattern,
        field_selectors=field_selectors,
        case_insensitive=options.case_insensitive,
        highlight_patterns=options.highlight_patterns,
        highlight_case_sensitive=options.highlight_case_sensitive,
        show_stats=options.show_stats,
        stats_only=options.stats_only,
        stats_json=options.stats_json,
    )
    console = Console()

    # Initialize statistics if needed (Phase 5)
    stats = None
    if config.show_stats or config.stats_only or config.stats_json:
        from tail_jsonl._private.stats import Statistics
        stats = Statistics()

    with fileinput.input() as _f:
        for line in _f:
            print_record(line, console, config, stats)

    # Print statistics at end if requested
    if stats:
        if config.stats_json:
            console.print(stats.to_json())
        else:
            stats.print_summary(console)
