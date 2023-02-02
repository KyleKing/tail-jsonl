"""Public CLI interface."""

import argparse
import fileinput
import sys
from pathlib import Path

from beartype import beartype
from beartype.typing import Dict, Optional
from rich.console import Console

from ._private.core import print_record
from .config import Config

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


@beartype
def _load_config(config_path: Optional[str]) -> Config:
    """Load specified configuration file."""
    user_config: Dict = {}  # type: ignore[type-arg]
    if config_path:
        user_config = tomllib.loads(Path(config_path).read_text())
    return Config(**user_config)


@beartype
def main() -> None:  # pragma: no cover
    """CLI Entrypoint."""
    # PLANNED: Add a flag (-v & store_true) to log debug information

    parser = argparse.ArgumentParser(description='Pipe JSONL Logs for pretty printing')
    parser.add_argument('--config-path', help='Path to a configuration file')
    options = parser.parse_args(sys.argv[1:])

    config = _load_config(options.config_path)
    console = Console()
    for line in fileinput.input():
        print_record(line, console, config)
