from enum import Enum
from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING

from pydantic import BaseModel, Field


class LogLevel(Enum):
    """Logging levels."""

    CRITICAL = CRITICAL
    ERROR = ERROR
    WARNING = WARNING
    INFO = INFO
    DEBUG = DEBUG
    NOTSET = NOTSET


class LoggerSettings(BaseModel):
    """Settings related to logger configuration."""

    name: str = Field(default="chattr", frozen=True)
    level: LogLevel = Field(default=LogLevel.INFO)
    propagate: bool = Field(default=False)
    format: str = Field(default="%(name)s | %(process)d | %(message)s")
