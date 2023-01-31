"""Public CLI interface."""

import argparse
import fileinput
import sys
from pathlib import Path
from typing import Dict

from beartype import beartype
from rich.console import Console

from ._private.core import print_record
from .config import Config

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


@beartype
def main() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    # PLANNED: Add a flag (-v & store_true) to log debug information

    parser = argparse.ArgumentParser(description='Pipe JSONL Logs for pretty printing')
    parser.add_argument('--config-path', help='Path to a configuration file')
    options = parser.parse_args(sys.argv[1:])

    user_config: Dict = {}  # type: ignore[type-arg]
    if options.config_path:
        tomllib.loads(Path(options.config_path).read_text())

    console = Console()
    config = Config(**user_config)
    for line in fileinput.input():
        print_record(line, console, config)
