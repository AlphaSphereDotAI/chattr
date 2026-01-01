from collections.abc import AsyncGenerator
from json import dumps
from typing import TYPE_CHECKING

from agno.agent import Agent, RunContentEvent, ToolCallCompletedEvent, ToolCallStartedEvent
from agno.models.message import Message
from agno.models.metrics import Metrics
from agno.models.response import ToolExecution
from agno.utils.log import configure_agno_logging
from gradio import Audio, Blocks, ChatInterface, ChatMessage, Dataframe, Error, Video
from gradio.components.chatbot import MetadataDict
from rich.pretty import pprint

from chattr.agent.agent import AgentConfiguration, setup_agent
from chattr.agent.database import setup_database
from chattr.agent.description import setup_description
from chattr.agent.instructions import setup_instructions
from chattr.agent.knowledge import setup_knowledge
from chattr.agent.model import setup_model
from chattr.agent.tools import close_mcp_tools, setup_mcp_tools
from chattr.agent.vector_database import setup_vector_database
from chattr.app.logger import logger
from chattr.app.settings import Settings

if TYPE_CHECKING:
    from agno.db.json import JsonDb
    from agno.knowledge import Knowledge
    from agno.models.openai import OpenAILike
    from agno.tools.mcp import MultiMCPTools
    from agno.vectordb.qdrant import Qdrant


class App:
    """Main application class for the Chattr Multi-agent system app."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Chattr app."""
        self.settings = settings

    def gradio_app(self) -> Blocks:
        """Create and return the main Gradio Blocks interface for the Chattr app."""
        return ChatInterface(
            fn=self.generate_response,
            save_history=True,
            title="Chattr",
            show_progress="full",
        )

    async def generate_response(
        self,
        message: str,
        history: list[ChatMessage | Audio | Video | Dataframe],
    ) -> AsyncGenerator[list[ChatMessage | Audio | Video | Dataframe]]:
        """
        Generate a response to a user message and update the conversation history.

        This asynchronous method streams responses from the state graph and
        yields updated history and audio file paths as needed.

        Args:
            message: The user's input message as a string.
            history: The conversation history as a list of ChatMessage objects.

        Returns:
            AsyncGenerator: Yields a list of the updated history containing
                            ChatMessage, Audio, and Video objects if it existed.
        """
        _tools: list[MultiMCPTools] | None = None
        tools: MultiMCPTools | None = await setup_mcp_tools(self.settings.mcp)
        model: OpenAILike = setup_model(self.settings.model)
        db: JsonDb = setup_database()
        vectordb: Qdrant = setup_vector_database(self.settings)
        knowledge: Knowledge = setup_knowledge(vectordb, db)
        description: str = setup_description(self.settings.character.name)
        instructions: list[str] = setup_instructions(self.settings.character.name, [tools])
        if not tools or len(tools.tools) == 0:
            _msg = "No tools found"
            logger.warning(_msg)
        else:
            _tools = [tools]
        configure_agno_logging(custom_default_logger=logger)
        agent: Agent = await setup_agent(
            AgentConfiguration(
                model=model,
                tools=_tools,
                description=description,
                instructions=instructions,
                db=db,
                knowledge=knowledge,
                timezone=self.settings.timezone,
                debug_mode=self.settings.debug,
            ),
        )
        async for response in agent.arun(
            Message(content=message, role="user"),
            stream=True,
            stream_events=True,
        ):
            pprint(response)
            if isinstance(response, RunContentEvent):
                history.append(ChatMessage(role="assistant", content=str(response.content)))
            elif isinstance(response, ToolCallStartedEvent):
                if not isinstance(response.tool, ToolExecution):
                    _msg = "ToolExecution expected"
                    logger.error(_msg)
                    raise TypeError(_msg)
                history.append(
                    ChatMessage(
                        role="assistant",
                        content=dumps(response.tool.tool_args, indent=4),
                        metadata=MetadataDict(
                            title=str(response.tool.tool_name),
                            id=str(response.tool.tool_call_id),
                            duration=response.tool.created_at,
                        ),
                    ),
                )
            elif isinstance(response, ToolCallCompletedEvent):
                if not isinstance(response.tool, ToolExecution):
                    _msg = "ToolExecution expected"
                    logger.error(_msg)
                    raise TypeError(_msg)
                if response.tool.tool_call_error:
                    if not isinstance(response.tool.metrics, Metrics):
                        _msg = "Metrics expected"
                        logger.error(_msg)
                        raise TypeError(_msg)
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(response.tool.tool_args, indent=4),
                            metadata=MetadataDict(
                                title=str(response.tool.tool_name),
                                id=str(response.tool.tool_call_id),
                                log="Tool Call Failed",
                                duration=float(str(response.tool.metrics.duration)),
                            ),
                        ),
                    )
                else:
                    if not isinstance(response.tool.metrics, Metrics):
                        _msg = "Metrics expected"
                        logger.error(_msg)
                        raise TypeError(_msg)
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(response.tool.tool_args, indent=4),
                            metadata=MetadataDict(
                                title=str(response.tool.tool_name),
                                id=str(response.tool.tool_call_id),
                                log="Tool Call Succeeded",
                                duration=float(str(response.tool.metrics.duration)),
                            ),
                        ),
                    )
                    if response.tool.tool_name == "generate_audio_for_text":
                        history.append(Audio(response.tool.result, autoplay=True))
                    elif response.tool.tool_name == "generate_video_mcp":
                        history.append(Video(response.tool.result, autoplay=True))
                    else:
                        _msg = f"Unknown tool name: {response.tool.tool_name}"
                        logger.error(_msg)
                        raise Error(_msg, print_exception=self.settings.debug)
            yield history
        await close_mcp_tools(tools)
