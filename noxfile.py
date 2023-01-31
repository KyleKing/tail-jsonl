"""nox-poetry configuration file."""

from calcipy.dev.noxfile import build_check, build_dist, coverage, pin_dev_dependencies, tests  # noqa: F401

# Ensure that non-calcipy dev-dependencies are available in Nox environments
pin_dev_dependencies([
    'pytest-cache-assert>=3.0.7',
    'pytest-pretty>=1.0.1',
    'tomli-w>=1.0.0',
])
