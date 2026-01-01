from agno.db.json import JsonDb


def setup_database() -> JsonDb:
    """
    Initialize the database for Chattr agent.

    Returns:
        JsonDb: The database for Chattr agent.
    """
    return JsonDb(db_path="agno")
