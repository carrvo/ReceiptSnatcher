"""Module for common functionality between other modules.
"""

import collections
from os import path
import logging

LOG = logging.getLogger(__name__)

# for logging
TRACE = 5
logging.addLevelName(TRACE, 'TRACE')
DEBUG = logging.DEBUG
INFO = logging.INFO
CONFIGURATION = 25
logging.addLevelName(CONFIGURATION, 'CONFIGURATION')
WARNING = logging.WARNING
#

APP_DATA = collections.namedtuple('AppData', [
    'appname', 'appauthor', 'version', 'user_data_dir', 'default_config'
])(
    'ReceiptSnatcher',
    'carrvo',
    None,
    path.expanduser("~/.local/share/ReceiptSnatcher/"),
    'config.rs'
)

class ConfigError(ValueError):
    """
    Raised when any configuration relating to the ReceiptSnatcher is invalid.
    """
    pass

__all__ = [
    'TRACE',
    'DEBUG',
    'INFO',
    'CONFIGURATION',
    'WARNING',
    'ConfigError',
]
