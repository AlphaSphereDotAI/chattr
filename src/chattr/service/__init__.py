"""Main application class for the Chattr Multi-agent system app."""

from typing import TYPE_CHECKING

from agno.agent import Agent
from agno.guardrails import PromptInjectionGuardrail
from agno.os import AgentOS, QueueConfig
from agno.tools.docling import DoclingTools

from chattr.character import DocQA, NapoleonBonaparte
from chattr.core import (
    AgentConfiguration,
    setup_agent,
    setup_database,
    setup_instructions,
    setup_knowledge,
    setup_mcp_tools,
    setup_model,
    setup_vector_database,
)
from chattr.service.queue import setup_queue
from chattr.settings import Settings

if TYPE_CHECKING:
    from agno.db import BaseDb
    from agno.knowledge import Knowledge
    from agno.models.openai import OpenAILike
    from agno.tools.mcp import MCPTools
    from agno.vectordb.qdrant import Qdrant


def setup_service(settings: Settings) -> AgentOS:
    tools: list[MCPTools] | None = setup_mcp_tools([
        settings.voice_generator_mcp_server,
        settings.video_generator_mcp_server,
        *settings.extra_mcp_servers,
    ])
    model: OpenAILike = setup_model(settings.model)
    db: BaseDb = setup_database()
    vectordb: Qdrant = setup_vector_database(settings.vector_database)
    knowledge: Knowledge = setup_knowledge(vectordb, db)
    instructions: list[str] = setup_instructions(tools)
    queue: QueueConfig = setup_queue(settings.queue)

    _agent_config = AgentConfiguration(
        model=model,
        tools=[*(tools or [])],
        db=db,
        knowledge=knowledge,
        instructions=instructions,
        pre_hooks=[PromptInjectionGuardrail()],
    )
    _docqa_config = AgentConfiguration(
        model=model,
        tools=[*(tools or []), DoclingTools(all=True)],
        db=db,
        knowledge=knowledge,
        instructions=instructions,
        pre_hooks=[PromptInjectionGuardrail()],
    )
    napoleon_bonaparte_agent: Agent = setup_agent(NapoleonBonaparte(), _agent_config, settings.agent)
    docqa_agent: Agent = setup_agent(DocQA(), _docqa_config, settings.agent)

    return AgentOS(
        name=settings.log.name.capitalize(),
        agents=[napoleon_bonaparte_agent, docqa_agent],
        db=db,
        tracing=True,
        queue=queue,
    )
