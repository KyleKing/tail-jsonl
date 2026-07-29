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
from ._private.completions import SHELLS, generate
from ._private.core import print_record
from .config import LEVEL_NAMES, Config, Filters, Render


def _load_config(
    config_path: str | None,
    *,
    debug: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    field_selectors: list[str] | None = None,
    case_insensitive: bool = False,
    min_level: str | None = None,
    local_time: bool = False,
    timestamp_format: str | None = None,
    hidden_keys: list[str] | None = None,
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
    config.render = Render(
        local_time=local_time or config.render.local_time,
        timestamp_format=timestamp_format or config.render.timestamp_format,
        hidden_keys=hidden_keys or config.render.hidden_keys,
    )
    return config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='tail-jsonl', description='Pipe JSONL Logs for pretty printing')
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
    parser.add_argument(
        '--local-time', action='store_true',
        help='Convert timestamps to the local timezone. Timestamps without a UTC offset are shown'
             ' unchanged, because the timezone they were written in is unknown',
    )
    parser.add_argument(
        '--timestamp-format', metavar='FORMAT',
        help='Render parsed timestamps with this strftime pattern, such as %%H:%%M:%%S.'
             ' Timestamps that cannot be parsed are always shown verbatim',
    )
    parser.add_argument(
        '--hide-key', action='append', dest='hidden_keys', metavar='KEY',
        help='Remove this dotted key from the rendered data. Repeat to hide several keys. Hiding a'
             ' key that is absent does nothing, and the timestamp, level, and message keys cannot'
             ' be hidden because they are rendered as their own fields',
    )
    parser.add_argument(
        '--completions', choices=SHELLS, metavar='SHELL',
        help=f'Print a completion script for one of ({", ".join(SHELLS)}) to stdout and exit,'
             ' such as eval "$(tail-jsonl --completions zsh)"',
    )
    return parser


def start() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    parser = _parser()
    options = parser.parse_args(sys.argv[1:])
    if options.completions:
        sys.stdout.write(generate(parser, options.completions))
        return
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
            local_time=options.local_time,
            timestamp_format=options.timestamp_format,
            hidden_keys=options.hidden_keys,
        )
    except (ValueError, re.error) as err:
        parser.error(str(err))
    console = Console()
    with fileinput.input() as f_:
        for line in f_:
            print_record(line, console, config)
