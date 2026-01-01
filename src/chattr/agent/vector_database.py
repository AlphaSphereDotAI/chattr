from agno.vectordb.qdrant import Qdrant

from chattr.app.settings import VectorDatabaseSettings


def setup_vector_database(vectordb: VectorDatabaseSettings) -> Qdrant:
    """
    Initialize a vector database connection.

    Args:
        vectordb (VectorDatabaseSettings): The settings required for
                                           connecting to the vector database.

    Returns:
        Qdrant: An instance of Qdrant configured with the specified vector database
                settings.
    """
    return Qdrant(collection=vectordb.name, url=vectordb.url.host, port=vectordb.url.port)
