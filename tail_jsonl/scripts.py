"""Start the command line program."""

import argparse
import fileinput
import sys
from pathlib import Path

from beartype import beartype
from beartype.typing import Dict, Optional
from corallium.tomllib import tomllib
from rich.console import Console

from . import __version__
from ._private.core import print_record
from .config import Config


@beartype
def _load_config(config_path: Optional[str]) -> Config:
    """Load specified configuration file."""
    user_config: Dict = {}  # type: ignore[type-arg]
    if config_path:
        user_config = tomllib.loads(Path(config_path).read_text(encoding='utf-8'))
    return Config(**user_config)


@beartype
def start() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    # PLANNED: Add a flag (--debug & store_true) to print debugging information

    parser = argparse.ArgumentParser(description='Pipe JSONL Logs for pretty printing')
    parser.add_argument(
        '-v', '--version', action='version',
        version=f'%(prog)s {__version__}', help="Show program's version number and exit.",
    )
    parser.add_argument('--config-path', help='Path to a configuration file')
    options = parser.parse_args(sys.argv[1:])
    sys.argv = sys.argv[:1]  # Remove CLI before calling fileinput

    config = _load_config(options.config_path)
    console = Console()
    for line in fileinput.input():
        print_record(line, console, config)
