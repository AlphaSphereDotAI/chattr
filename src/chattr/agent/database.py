from agno.db.json import JsonDb


def setup_database() -> JsonDb:
    return JsonDb(
        db_path="agno",
    )
