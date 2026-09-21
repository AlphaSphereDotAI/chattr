"""Main application class for the Chattr Multi-agent system app."""

from typing import TYPE_CHECKING

from agno.agent import Agent
from agno.os import AgentOS

from chattr.agent.agent import AgentConfiguration, setup_agent
from chattr.agent.database import setup_database
from chattr.agent.description import setup_description
from chattr.agent.instructions import setup_instructions
from chattr.agent.knowledge import setup_knowledge
from chattr.agent.model import setup_model
from chattr.agent.tools import setup_mcp_tools
from chattr.agent.vector_database import setup_vector_database
from chattr.settings import Settings

if TYPE_CHECKING:
    from agno.db.json import JsonDb
    from agno.knowledge import Knowledge
    from agno.models.openai import OpenAILike
    from agno.tools.mcp import MCPTools
    from agno.vectordb.qdrant import Qdrant


def setup_app(settings: Settings) -> AgentOS:
    tools: list[MCPTools] | None = setup_mcp_tools(
        [
            settings.voice_generator_mcp_server,
            settings.video_generator_mcp_server,
            *settings.extra_mcp_servers,
        ]
    )
    model: OpenAILike = setup_model(settings.model)
    db: JsonDb = setup_database()
    vectordb: Qdrant = setup_vector_database(settings.vector_database)
    knowledge: Knowledge = setup_knowledge(vectordb, db)
    description: str = setup_description(settings.character.name)
    instructions: list[str] = setup_instructions(settings.character.name, tools)

    agent: Agent = setup_agent(
        AgentConfiguration(
            model=model,
            tools=tools if tools else [],
            description=description,
            instructions=instructions,
            db=db,
            knowledge=knowledge,
            timezone=settings.timezone,
            debug_mode=settings.debug,
        ),
    )

    return AgentOS(name=settings.log.name.capitalize(), agents=[agent], db=db)
