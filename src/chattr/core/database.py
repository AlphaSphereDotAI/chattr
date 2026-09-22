"""A module for initializing the database for the Chattr agent."""

from agno.db import BaseDb
from agno.db.json import JsonDb


def setup_database() -> BaseDb:
    """
    Initialize the database for Chattr agent.

    Returns:
        JsonDb: The database for Chattr agent.
    """
    return JsonDb(db_path="agno")
