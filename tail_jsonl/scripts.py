"""Start the command line program."""

from __future__ import annotations

import argparse
import fileinput
import re
import sys
from pathlib import Path

from corallium.tomllib import tomllib
from rich.console import Console

from . import __version__
from ._private.core import print_record
from .config import LEVEL_NAMES, Config, Filters


def _load_config(
    config_path: str | None,
    *,
    debug: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    field_selectors: list[str] | None = None,
    case_insensitive: bool = False,
    min_level: str | None = None,
) -> Config:
    """Return loaded specified configuration file, where CLI arguments win over file values."""
    user_config: dict = {}  # type: ignore[type-arg]
    if config_path:
        pth = Path(config_path).expanduser()
        user_config = tomllib.loads(pth.read_text(encoding='utf-8'))
    config = Config.from_dict(user_config)
    # CLI debug flag overrides config file
    if debug:
        config.debug = True
    config.filters = Filters(
        include=include or config.filters.include,
        exclude=exclude or config.filters.exclude,
        field_selectors=field_selectors or config.filters.field_selectors,
        case_insensitive=case_insensitive or config.filters.case_insensitive,
        min_level=min_level or config.filters.min_level,
    )
    return config


def _parser() -> argparse.ArgumentParser:
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
    parser.add_argument(
        '-i', '--include', action='append', metavar='PATTERN',
        help='Only show raw lines matching this regex. Repeat to match any of several patterns',
    )
    parser.add_argument(
        '-e', '--exclude', action='append', metavar='PATTERN',
        help='Drop raw lines matching this regex. Repeat to drop any of several patterns.'
             ' Takes precedence over --include',
    )
    parser.add_argument(
        '--field-selector', action='append', dest='field_selectors', metavar='KEY=PATTERN',
        help='Only show records whose dotted KEY matches this regex. Repeat to require every selector.'
             ' Records missing KEY are dropped, but lines that are not valid JSON are always printed',
    )
    parser.add_argument(
        '--case-insensitive', action='store_true',
        help='Match every pattern without regard to case',
    )
    parser.add_argument(
        '-l', '--min-level', choices=LEVEL_NAMES, type=str.lower,
        help='Drop records below this level. Records with an unrecognized or missing level are kept,'
             ' as are lines that are not valid JSON',
    )
    return parser


def start() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    parser = _parser()
    options = parser.parse_args(sys.argv[1:])
    sys.argv = sys.argv[:1]  # Remove CLI before calling fileinput

    try:
        config = _load_config(
            options.config_path,
            debug=options.debug,
            include=options.include,
            exclude=options.exclude,
            field_selectors=options.field_selectors,
            case_insensitive=options.case_insensitive,
            min_level=options.min_level,
        )
    except (ValueError, re.error) as err:
        parser.error(str(err))
    console = Console()
    with fileinput.input() as f_:
        for line in f_:
            print_record(line, console, config)
