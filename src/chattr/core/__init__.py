from chattr.core.agent import AgentConfiguration, setup_agent
from chattr.core.database import setup_database
from chattr.core.embedder import setup_embedder
from chattr.core.instructions import setup_instructions
from chattr.core.knowledge import setup_knowledge
from chattr.core.logger import setup_logger
from chattr.core.model import setup_model
from chattr.core.tools import setup_mcp_tools
from chattr.core.vector_database import setup_vector_database

__all__ = [
    "AgentConfiguration",
    "setup_agent",
    "setup_database",
    "setup_embedder",
    "setup_instructions",
    "setup_knowledge",
    "setup_logger",
    "setup_mcp_tools",
    "setup_model",
    "setup_vector_database",
]
