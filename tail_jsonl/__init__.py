"""tail_jsonl."""

from warnings import filterwarnings

from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from loguru import logger  # noqa: F401

__version__ = '1.0.0'
__pkg_name__ = 'tail_jsonl'

# ====== Above is the recommended code from calcipy_template and may be updated on new releases ======

# FYI: https://github.com/beartype/beartype#are-we-on-the-worst-timeline
filterwarnings('ignore', category=BeartypeDecorHintPep585DeprecationWarning)

from .main import main  # noqa: F401
