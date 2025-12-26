"""A module for configuring and initializing."""

from warnings import filterwarnings

from rich.console import Console

filterwarnings("ignore", category=DeprecationWarning)

console = Console()
APP_NAME: str = str(__package__)
