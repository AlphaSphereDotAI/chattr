from warnings import filterwarnings

from rich.console import Console

filterwarnings("ignore", category=DeprecationWarning)

console = Console()
