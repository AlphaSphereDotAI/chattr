"""A module for configuring and initializing."""

from logging import Logger
from warnings import filterwarnings

from agno.utils.log import configure_agno_logging

from chattr.app.logger import setup_logger

filterwarnings("ignore", category=DeprecationWarning)
logger: Logger = setup_logger(__package__)
configure_agno_logging(custom_default_logger=logger)
