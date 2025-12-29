"""Main orchestration graph for the Chattr application."""

from textwrap import dedent

from agno.agent import Agent
from agno.guardrails import PromptInjectionGuardrail
from gradio import Error
from rich.pretty import pprint

from chattr.agent.database import setup_database
from chattr.agent.knowledge import setup_knowledge
from chattr.agent.model import setup_model
from chattr.agent.tools import setup_mcp_tools
from chattr.agent.vector_database import setup_vector_database
from chattr.app.logger import logger
from chattr.app.settings import Settings


async def setup_agent(settings: Settings) -> Agent:
    """Initialize the Chattr agent."""
    try:
        model = setup_model(settings)
        tools = await setup_mcp_tools(settings)
        db = setup_database()
        vectordb = setup_vector_database(settings)
        knowledge = setup_knowledge(vectordb, db)
        description = dedent(
            f"""
            You are a helpful assistant
            who can act and mimic {settings.character.name}'s character
            and answer questions about the era.
            """
        )
        instructions = [
            "Understand the user's question and context.",
            "Gather relevant information and resources.",
            f"Formulate a clear and concise response in {settings.character.name}'s voice.",
        ]
        for tool in tools:
            for key in tool.functions:
                # pprint(tool.functions[key])
                if tool.functions[key].name == "generate_audio_for_text":
                    instructions.append(
                        "Generate audio from the formulated response using the appropriate Tool."
                    )
                if tool.functions[key].name == "generate_video_mcp":
                    instructions.append(
                        "Generate video from the resulted audio using the appropriate Tool."
                    )
        return Agent(
            model=model,
            tools=tools,
            description=description,
            instructions=instructions,
            db=db,
            knowledge=knowledge,
            markdown=True,
            add_datetime_to_context=True,
            timezone_identifier=settings.timezone,
            pre_hooks=[PromptInjectionGuardrail()],
            debug_mode=True,
            save_response_to_file="agno/response.txt",
            add_history_to_context=True,
            add_memories_to_context=True,
        )
    except ValueError as e:
        _msg: str = f"Failed to initialize Agent: {e}"
        logger.error(_msg)
        raise Error(_msg, print_exception=settings.debug) from e
