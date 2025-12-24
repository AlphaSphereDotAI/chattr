from logging import INFO, WARNING, FileHandler, Logger, basicConfig, getLogger
from pathlib import Path

from rich.logging import RichHandler

from chattr import APP_NAME, console

basicConfig(
    level=INFO,
    handlers=[
        RichHandler(
            level=INFO,
            console=console,
            rich_tracebacks=True,
        ),
        FileHandler(Path.cwd() / "logs" / APP_NAME / "chattr.log", delay=True),
    ],
    format="%(name)s | %(process)d | %(message)s",
)
getLogger("httpx").setLevel(WARNING)
logger: Logger = getLogger(APP_NAME)
