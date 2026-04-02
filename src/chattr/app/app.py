"""Main application class for the Chattr Multi-agent system app."""

from typing import TYPE_CHECKING

from agno.agent import Agent
from agno.os import AgentOS
from agno.utils.log import log_warning

from chattr.agent.agent import AgentConfiguration, setup_agent
from chattr.agent.database import setup_database
from chattr.agent.description import setup_description
from chattr.agent.instructions import setup_instructions
from chattr.agent.knowledge import setup_knowledge
from chattr.agent.model import setup_model
from chattr.agent.tools import setup_mcp_tools
from chattr.agent.vector_database import setup_vector_database
from chattr.app.settings import Settings

if TYPE_CHECKING:
    from agno.db.json import JsonDb
    from agno.knowledge import Knowledge
    from agno.models.openai import OpenAILike
    from agno.tools.mcp import MultiMCPTools
    from agno.vectordb.qdrant import Qdrant


def setup_app(settings: Settings) -> AgentOS:
    _tools: list[MultiMCPTools] | None = None
    tools: MultiMCPTools | None = setup_mcp_tools(settings.mcp)
    model: OpenAILike = setup_model(settings.model)
    db: JsonDb = setup_database()
    vectordb: Qdrant = setup_vector_database(settings.vector_database)
    knowledge: Knowledge = setup_knowledge(vectordb, db)
    description: str = setup_description(settings.character.name)
    instructions: list[str] = setup_instructions(settings.character.name, [tools])

    if not tools or len(tools.tools) == 0:
        _msg = "No tools found"
        log_warning(_msg)
    else:
        _tools = [tools]

    agent: Agent = setup_agent(
        AgentConfiguration(
            model=model,
            tools=_tools,
            description=description,
            instructions=instructions,
            db=db,
            knowledge=knowledge,
            timezone=settings.timezone,
            debug_mode=settings.debug,
        ),
    )

    return AgentOS(name=settings.log.name.capitalize(), agents=[agent], db=db)
