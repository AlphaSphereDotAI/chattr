"""Main orchestration graph for the Chattr application."""

from collections.abc import AsyncGenerator
from json import dumps
from pathlib import Path

from agno.agent import (
    Agent,
    RunContentEvent,
    ToolCallCompletedEvent,
    ToolCallStartedEvent,
)
from agno.db import BaseDb
from agno.db.json import JsonDb
from agno.knowledge.knowledge import Knowledge
from agno.models.message import Message
from agno.models.openai.like import OpenAILike
from agno.tools import Toolkit
from agno.tools.mcp import MultiMCPTools
from agno.vectordb.qdrant import Qdrant
from gradio import (
    Audio,
    Blocks,
    ChatInterface,
    ChatMessage,
    Error,
    Video,
)
from gradio.components.chatbot import MetadataDict
from m3u8 import M3U8, load
from poml import poml
from pydantic import HttpUrl, ValidationError
from requests import Session
from rich.pretty import pprint

from chattr.app.settings import Settings, logger


class App:
    """Main application class for the Chattr Multi-agent system app."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def _setup_agent(self) -> Agent:
        return Agent(
            model=self._setup_model(),
            tools=await self._setup_tools(),
            description="You are a helpful assistant who can act and mimic Napoleon's character and answer questions about the era.",
            instructions=[
                "Understand the user's question and context.",
                "Gather relevant information and resources.",
                "Formulate a clear and concise response in Napoleon's voice.",
                "ALWAYS generate audio from the formulated response using the appropriate Tool.",
                "Generate video from the resulted audio using the appropriate Tool.",
            ],
            db=self._setup_database(),
            knowledge=self._setup_knowledge(
                self._setup_vector_database(),
                self._setup_database(),
            ),
            markdown=True,
            add_datetime_to_context=True,
            timezone_identifier="Africa/Cairo",
            # pre_hooks=[PIIDetectionGuardrail(), PromptInjectionGuardrail()],
            # debug_mode=True,
            save_response_to_file="agno/response.txt",
            add_history_to_context=True,
            add_memories_to_context=True,
        )

    async def _setup_tools(self) -> list[Toolkit]:
        self.mcp_tools = MultiMCPTools(
            urls=[
                "http://localhost:7861/gradio_api/mcp/",
                "http://localhost:7862/gradio_api/mcp/?tools=generate_video_mcp",
            ],
            urls_transports=["streamable-http", "streamable-http"],
        )
        await self.mcp_tools.connect()
        return [self.mcp_tools]

    def _setup_prompt(self) -> str:
        prompt_template = poml(
            self.settings.directory.prompts / "template.poml",
            {"character": "Napoleon"},
            chat=False,
            format="dict",
        )
        if not isinstance(prompt_template, dict):
            _msg = "Prompt template must be a string."
            raise TypeError(_msg)
        return prompt_template["messages"]

    def _setup_model(self) -> OpenAILike:
        """
        Initialize the ChatOpenAI language model using the provided settings.

        This method creates and returns a ChatOpenAI instance configured with
        the model's URL, name, API key, and temperature.

        Returns:
            ChatOpenAI: The initialized ChatOpenAI language model instance.

        Raises:
            Exception: If the model initialization fails.
        """
        try:
            return OpenAILike(
                base_url=str(self.settings.model.url),
                id=self.settings.model.name,
                api_key=self.settings.model.api_key.get_secret_value(),
                temperature=self.settings.model.temperature,
            )
        except Exception as e:
            _msg: str = f"Failed to initialize ChatOpenAI model: {e}"
            logger.error(_msg)
            raise Error(_msg) from e

    def _setup_vector_database(self) -> Qdrant:
        return Qdrant(
            collection=self.settings.vector_database.name,
            url=self.settings.vector_database.url.host,
        )

    def _setup_knowledge(self, vector_db: Qdrant, db: BaseDb) -> Knowledge:
        return Knowledge(
            vector_db=vector_db,
            contents_db=db,
        )

    def _setup_database(self) -> JsonDb:
        return JsonDb(
            db_path="agno",
        )

    def gui(self) -> Blocks:
        """
        Create and return the main Gradio Blocks interface for the Chattr app.

        Returns:
            Blocks: The constructed Gradio Blocks interface for the chat application.
        """
        return ChatInterface(
            fn=self.generate_response, type="messages", save_history=True
        )

    async def generate_response(
        self,
        message: str,
        history: list[ChatMessage],
    ) -> AsyncGenerator[tuple[str, list[ChatMessage], Path | None, Path | None]]:
        """
        Generate a response to a user message and update the conversation history.

        This asynchronous method streams responses from the state graph and
        yields updated history and audio file paths as needed.

        Args:
            message: The user's input message as a string.
            history: The conversation history as a list of ChatMessage objects.

        Returns:
            AsyncGenerator: Yields a tuple containing an
                            empty string, the updated history, and
                            a Path to an audio file if generated.
        """
        try:
            agent: Agent = await self._setup_agent()
            async for response in agent.arun(
                Message(content=message, role="user"),
                stream=True,
            ):
                pprint(response)
                if isinstance(response, RunContentEvent):
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=response.content,
                        ),
                    )
                elif isinstance(response, ToolCallStartedEvent):
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(response.tool.tool_args, indent=4),
                            metadata=MetadataDict(
                                title=response.tool.tool_name,
                                id=response.tool.tool_call_id,
                                duration=response.tool.created_at,
                            ),
                        ),
                    )
                elif isinstance(response, ToolCallCompletedEvent):
                    if response.tool.tool_call_error:
                        history.append(
                            ChatMessage(
                                role="assistant",
                                content=dumps(response.tool.tool_args, indent=4),
                                metadata=MetadataDict(
                                    title=response.tool.tool_name,
                                    id=response.tool.tool_call_id,
                                    log="Tool Call Failed",
                                    duration=response.tool.metrics.duration,
                                ),
                            ),
                        )
                    else:
                        history.append(
                            ChatMessage(
                                role="assistant",
                                content=dumps(response.tool.tool_args, indent=4),
                                metadata=MetadataDict(
                                    title=response.tool.tool_name,
                                    id=response.tool.tool_call_id,
                                    log="Tool Call Succeeded",
                                    duration=response.tool.metrics.duration,
                                ),
                            ),
                        )
                        if response.tool.tool_name == "generate_audio_for_text":
                            history.append(
                                Audio(
                                    response.tool.result,
                                    autoplay=True,
                                    show_download_button=True,
                                    show_share_button=True,
                                ),
                            )
                        elif response.tool.tool_name == "generate_video_mcp":
                            history.append(
                                Video(
                                    response.tool.result,
                                    autoplay=True,
                                    show_download_button=True,
                                    show_share_button=True,
                                ),
                            )
                        else:
                            msg = f"Unknown tool name: {response.tool.tool_name}"
                            raise Error(msg)
                yield history
        except Exception as e:
            _msg: str = f"Error generating response: {e}"
            logger.error(_msg)
            raise Error(_msg) from e
        finally:
            await self._close()

    def _is_url(self, value: str | None) -> bool:
        """
        Check if a string is a valid URL.

        Args:
            value: The string to check. Can be None.

        Returns:
            bool: True if the string is a valid URL, False otherwise.
        """
        if value is None:
            return False

        try:
            _ = HttpUrl(value)
        except ValidationError:
            return False
        return True

    def _download_file(self, url: HttpUrl, path: Path) -> None:
        """
        Download a file from a URL and save it to a local path.

        Args:
            url: The URL to download the file from.
            path: The local file path where the downloaded file will be saved.

        Returns:
            None

        Raises:
            requests.RequestException: If the HTTP request fails.
            IOError: If file writing fails.
        """
        if str(url).endswith(".m3u8"):
            _playlist: M3U8 = load(url)
            url: str = str(url).replace("playlist.m3u8", _playlist.segments[0].uri)
        logger.info(f"Downloading {url} to {path}")
        session = Session()
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"File downloaded to {path}")

    async def _close(self) -> None:
        try:
            logger.info("Closing MCP tools...")
            await self.mcp_tools.close()
        except Exception as e:
            msg: str = (
                f"Error closing MCP tools: {e}, Check if the Tool services are running."
            )
            logger.error(msg)
            raise Error(msg) from e


async def test() -> None:
    from chattr.app.builder import App
    from chattr.app.settings import Settings

    settings: Settings = Settings()
    app: App = App(settings)
    agent: Agent = await app._setup_agent()
    try:
        await agent.aprint_response("Hello!", debug_mode=True)
    finally:
        await app._close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
