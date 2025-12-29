from agno.vectordb.qdrant import Qdrant

from chattr.app.settings import Settings


def setup_vector_database(settings: Settings) -> Qdrant:
    return Qdrant(
        collection=settings.vector_database.name,
        url=settings.vector_database.url.host,
    )
