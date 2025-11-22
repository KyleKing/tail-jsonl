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


def _load_config(config_path: str | None, *, debug: bool = False) -> Config:
    """Return loaded specified configuration file."""
    user_config: dict = {}  # type: ignore[type-arg]
    if config_path:
        pth = Path(config_path).expanduser()
        user_config = tomllib.loads(pth.read_text(encoding='utf-8'))
    config = Config.from_dict(user_config)
    # CLI debug flag overrides config file
    if debug:
        config.debug = True
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
    options = parser.parse_args(sys.argv[1:])
    sys.argv = sys.argv[:1]  # Remove CLI before calling fileinput

    config = _load_config(options.config_path, debug=options.debug)
    console = Console()
    with fileinput.input() as _f:
        for line in _f:
            print_record(line, console, config)
