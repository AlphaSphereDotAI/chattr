from agno.db import BaseDb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant


def setup_knowledge(vector_db: Qdrant, db: BaseDb) -> Knowledge:
    return Knowledge(
        vector_db=vector_db,
        contents_db=db,
    )
