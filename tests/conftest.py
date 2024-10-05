"""Pytest configuration."""

from pathlib import Path

import pytest
from rich.console import Console

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture
def console():
    console = Console(log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    return console
