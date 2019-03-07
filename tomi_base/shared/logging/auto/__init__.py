import logging
from enum import Enum


class When(Enum):
    BEFORE = "before",
    AFTER = "after",
    OTHER = "other",
    NOTSET = "never"


class LoggerLevel(Enum):
    CRITICAL = logging.CRITICAL,
    FATAL = logging.FATAL,
    ERROR = logging.ERROR,
    WARNING = logging.WARNING,
    WARN = logging.WARN,
    INFO = logging.INFO,
    DEBUG = logging.DEBUG,
    NOTSET = logging.NOTSET
