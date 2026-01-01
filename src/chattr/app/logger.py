"""A module handles the configuration of logging for the application."""

from logging import INFO, Formatter, Logger, getLogger

from rich.console import Console
from rich.logging import RichHandler


def setup_logger(logger_name: str | None) -> Logger:
    logger: Logger = getLogger(logger_name)
    console = Console()
    handler = RichHandler(level=INFO, console=console, rich_tracebacks=True)
    formatter = Formatter("%(name)s | %(process)d | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(INFO)
    logger.propagate = False
    return logger
