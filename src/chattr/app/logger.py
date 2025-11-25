from logging import DEBUG, INFO, WARNING, basicConfig, getLogger, Logger

from rich.logging import RichHandler

from chattr import console, APP_NAME

basicConfig(
    level=DEBUG,  # INFO,
    handlers=[
        RichHandler(
            level=INFO,
            console=console,
            rich_tracebacks=True,
        ),
    ],
    format="%(name)s | %(process)d | %(message)s",
)
getLogger("httpx").setLevel(WARNING)
logger: Logger = getLogger(APP_NAME)
