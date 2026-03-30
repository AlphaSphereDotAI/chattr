from sys import exit as sys_exit

from agno.db import BaseDb
from agno.knowledge.knowledge import Knowledge
from agno.utils.log import log_error
from agno.vectordb.qdrant import Qdrant
from qdrant_client.http.exceptions import ResponseHandlingException


def setup_knowledge(vector_db: Qdrant, db: BaseDb) -> Knowledge:
    """Set up the knowledge for the agent."""
    try:
        vector_db.client.get_collections()
    except ResponseHandlingException:
        log_error("Cannot reach Qdrant. Ensure it is running and accessible.")
        sys_exit(1)
    return Knowledge(vector_db=vector_db, contents_db=db)
