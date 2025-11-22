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
    context_before: int = 0,
    context_after: int = 0,
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

    # CLI flags for context lines (Phase 7)
    if context_before > 0:
        config.context_before = context_before
    if context_after > 0:
        config.context_after = context_after

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

    # Phase 7: Context lines flags
    parser.add_argument(
        '-B', '--before-context',
        type=int,
        default=0,
        metavar='N',
        help='Print N lines of leading context before matches',
    )
    parser.add_argument(
        '-A', '--after-context',
        type=int,
        default=0,
        metavar='N',
        help='Print N lines of trailing context after matches',
    )
    parser.add_argument(
        '-C', '--context',
        type=int,
        metavar='N',
        help='Print N lines of context before and after matches (overrides -A and -B)',
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

    # Handle context option (-C overrides -A and -B)
    context_before = options.before_context
    context_after = options.after_context
    if options.context is not None:
        context_before = options.context
        context_after = options.context

    config = _load_config(
        options.config_path,
        debug=options.debug,
        include_pattern=options.include_pattern,
        exclude_pattern=options.exclude_pattern,
        field_selectors=field_selectors,
        case_insensitive=options.case_insensitive,
        context_before=context_before,
        context_after=context_after,
    )
    console = Console()
    with fileinput.input() as _f:
        for line in _f:
            print_record(line, console, config)
