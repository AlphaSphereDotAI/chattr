"""Main orchestration graph for the Chattr application."""

from agno.agent import Agent
from agno.db import BaseDb
from agno.guardrails import PromptInjectionGuardrail
from agno.knowledge import Knowledge
from agno.models.openai import OpenAILike
from agno.tools.mcp import MultiMCPTools


async def setup_agent(
    model: OpenAILike,
    tools: list[MultiMCPTools] | None,
    description: str,
    instructions: list[str],
    db: BaseDb,
    knowledge: Knowledge,
    timezone: str,
) -> Agent:
    """Initialize the Chattr agent."""
    return Agent(
        model=model,
        tools=tools,
        description=description,
        instructions=instructions,
        db=db,
        knowledge=knowledge,
        markdown=True,
        add_datetime_to_context=True,
        timezone_identifier=timezone,
        pre_hooks=[PromptInjectionGuardrail()],
        debug_mode=True,
        save_response_to_file="agno/response.txt",
        add_history_to_context=True,
        add_memories_to_context=True,
    )
