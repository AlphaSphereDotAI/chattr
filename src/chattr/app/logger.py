from logging import INFO, WARNING, FileHandler, basicConfig, getLogger
from pathlib import Path

from rich.logging import RichHandler

from chattr import console

basicConfig(
    level=INFO,
    handlers=[
        RichHandler(
            level=INFO,
            console=console,
            rich_tracebacks=True,
        ),
        FileHandler(Path.cwd() / "logs" / "langgraph.log"),
    ],
    format="%(name)s | %(process)d | %(message)s",
)
getLogger("httpx").setLevel(WARNING)
logger = getLogger(__package__)
