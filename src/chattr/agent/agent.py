"""Main orchestration graph for the Chattr application."""

from typing import NamedTuple

from agno.agent import Agent
from agno.db import BaseDb
from agno.guardrails import PromptInjectionGuardrail
from agno.knowledge import Knowledge
from agno.models.openai import OpenAILike
from agno.tools.mcp import MultiMCPTools


class AgentConfiguration(NamedTuple):
    """Configuration class for the Chattr agent."""

    model: OpenAILike
    tools: list[MultiMCPTools] | None
    description: str
    instructions: list[str]
    db: BaseDb
    knowledge: Knowledge
    timezone: str
    debug_mode: bool


async def setup_agent(agent_config: AgentConfiguration) -> Agent:
    """
    Initialize the Chattr agent.

    Args:
        agent_config (AgentConfiguration): Agent configuration.

    Returns:
        Agent: The Chattr agent.
    """
    return Agent(
        model=agent_config.model,
        tools=agent_config.tools,
        description=agent_config.description,
        instructions=agent_config.instructions,
        db=agent_config.db,
        knowledge=agent_config.knowledge,
        markdown=True,
        add_datetime_to_context=True,
        timezone_identifier=agent_config.timezone,
        pre_hooks=[PromptInjectionGuardrail()],
        debug_mode=agent_config.debug_mode,
        save_response_to_file="agno/response.txt",
        add_history_to_context=True,
        add_memories_to_context=True,
    )
