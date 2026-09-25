"""Main orchestration graph for the Chattr application."""
from collections.abc import Callable
from typing import Any, NamedTuple

from agno.agent import Agent
from agno.db import BaseDb
from agno.eval import BaseEval
from agno.guardrails import BaseGuardrail
from agno.knowledge import Knowledge
from agno.models.base import Model
from agno.tools import Toolkit

from chattr.character import Character
from chattr.settings import AgentSettings


class AgentConfiguration(NamedTuple):
    """Configuration class for the Chattr agent."""

    model: Model
    tools: list[Toolkit]
    db: BaseDb
    knowledge: Knowledge
    instructions: list[str]
    pre_hooks: list[Callable[..., Any] | BaseGuardrail | BaseEval] | None


def setup_agent(persona: Character, agent_config: AgentConfiguration, settings: AgentSettings) -> Agent:
    """
    Initialize the Chattr agent.

    Args:
        agent_config (AgentConfiguration): Agent configuration.

    Returns:
        Agent: The Chattr agent.
    """
    return Agent(
        name=persona.name,
        description=persona.description,
        instructions=agent_config.instructions + persona.instructions,
        model=agent_config.model,
        tools=agent_config.tools,
        db=agent_config.db,
        knowledge=agent_config.knowledge,
        pre_hooks=agent_config.pre_hooks,
        markdown=settings.markdown,
        add_datetime_to_context=settings.add_datetime_to_context,
        timezone_identifier=settings.timezone_identifier,
        debug_mode=settings.debug_mode,
        save_response_to_file=settings.save_response_to_file.as_posix(),
        add_history_to_context=settings.add_history_to_context,
        add_memories_to_context=settings.add_memories_to_context,
        enable_agentic_state=settings.enable_agentic_state,
        cache_session=settings.cache_session,
        checkpoint=settings.checkpoint,
        enable_agentic_memory=settings.enable_agentic_memory,
        update_memory_on_run=settings.update_memory_on_run,
        enable_session_summaries=settings.enable_session_summaries,
        add_session_summary_to_context=settings.add_session_summary_to_context,
        compress_tool_results=settings.compress_tool_results,
        num_history_runs=settings.num_history_runs,
        num_history_messages=settings.num_history_messages,
        enable_agentic_knowledge_filters=settings.enable_agentic_knowledge_filters,
        add_knowledge_to_context=settings.add_knowledge_to_context,
        tool_call_limit=settings.tool_call_limit,
        max_tool_calls_from_history=settings.max_tool_calls_from_history,
        read_chat_history=settings.read_chat_history,
        search_knowledge=settings.search_knowledge,
        add_search_knowledge_instructions=settings.add_search_knowledge_instructions,
        update_knowledge=settings.update_knowledge,
        read_tool_call_history=settings.read_tool_call_history,
        send_media_to_model=settings.send_media_to_model,
        store_media=settings.store_media,
        store_tool_messages=settings.store_tool_messages,
        store_history_messages=settings.store_history_messages,
        retries=settings.retries,
        delay_between_retries=settings.delay_between_retries,
        structured_outputs=settings.structured_outputs,
        use_json_mode=settings.use_json_mode,
        cache_callables=settings.cache_callables,
    )
