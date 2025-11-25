from logging import DEBUG, INFO, WARNING, Logger, basicConfig, getLogger

from rich.logging import RichHandler

from chattr import APP_NAME, console

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
