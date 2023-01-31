"""Public CLI interface."""

import fileinput

from beartype import beartype
from rich.console import Console

from ._private.config import Config
from ._private.core import print_record


@beartype
def main() -> None:
    """CLI Entrypoint."""
    console = Console()
    # PLANNED: Support configuration with argparse or environment variable
    config = Config()
    for line in fileinput.input():
        print_record(line, console, config)
