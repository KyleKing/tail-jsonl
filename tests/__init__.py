import sys
from os import environ, getenv

# Required for consistent test output
environ['COLUMNS'] = '120'

DEF_MODE = 'ERROR' if sys.version_info >= (3, 10) else 'WARNING'
environ['RUNTIME_TYPE_CHECKING_MODE'] = getenv('RUNTIME_TYPE_CHECKING_MODE', DEF_MODE)
