"""A module for configuring and initializing."""

from warnings import filterwarnings

from rich.console import Console

filterwarnings("ignore", category=DeprecationWarning)
logger: Logger = setup_logger(__package__)
configure_agno_logging(custom_default_logger=logger)
