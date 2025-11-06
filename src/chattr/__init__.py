from warnings import filterwarnings

from rich.console import Console

filterwarnings("ignore", category=DeprecationWarning)

console = Console()
APP_NAME: str = __package__
