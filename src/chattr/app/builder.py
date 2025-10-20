"""Main orchestration graph for the Chattr application."""

from json import dumps, loads
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Self

from deepagents import create_deep_agent
from gradio import (
    Audio,
    Blocks,
    Button,
    Chatbot,
    ChatMessage,
    ClearButton,
    Column,
    Error,
    Image,
    Markdown,
    Row,
    Sidebar,
    Textbox,
    Video,
)
from gradio.components.chatbot import MetadataDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompt_values import StringPromptValue
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai.chat_models.base import BaseChatModel
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from langgraph.graph.state import CompiledStateGraph
from m3u8 import M3U8, load
from poml.integration.langchain import LangchainPomlTemplate
from pydantic import FilePath, HttpUrl, ValidationError
from requests import Session

from chattr.app.settings import Settings, logger
from chattr.app.state import State

if TYPE_CHECKING:
    from langchain_mcp_adapters.sessions import Connection


class App:
    """Main application class for the Chattr Multi-agent system app."""

    settings: Settings
    _tools: list[BaseTool]
    _checkpointer: AsyncMongoDBSaver
    _deep_agent: CompiledStateGraph

    @classmethod
    async def create(cls, settings: Settings) -> Self:
        """Async factory method to create a Graph instance."""
        cls.settings = settings
        cls._tools = []
        try:
            mcp_config: dict[str, Connection] = loads(
                cls.settings.mcp.path.read_text(encoding="utf-8"),
            )
            cls._tools = await cls._setup_tools(MultiServerMCPClient(mcp_config))
        except OSError as e:
            logger.warning(f"Failed to read MCP config file: {e}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse MCP config JSON: {e}")
        except Exception as e:
            logger.warning(f"Failed to setup MCP tools: {e}")
        cls._checkpointer = AsyncMongoDBSaver.from_conn_string("localhost:27017")
        cls._deep_agent = cls._setup_deepagents()
        return cls()

    @classmethod
    def _setup_deepagents(cls) -> CompiledStateGraph:
        """Return the DeepAgents multi-agent system graph."""
        return create_deep_agent(
            model=cls._setup_model(),
            system_prompt=cls._setup_prompt(),
            tools=cls._tools,
            checkpointer=cls._checkpointer,
            use_longterm_memory=True,
        )

    @classmethod
    def _setup_prompt(cls) -> str:
        prompt_template = LangchainPomlTemplate.from_file(
            cls.settings.directory.prompts / "template.poml",
            speaker_mode=False,
        )
        prompt = prompt_template.format(character="Napoleon")
        if not isinstance(prompt, StringPromptValue):
            msg = "Prompt must be a StringPromptValue in non-speaker mode."
            raise TypeError(msg)
        return prompt.to_string()

    @classmethod
    def _setup_model(cls) -> BaseChatModel:
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
            return init_chat_model("gemini-2.5-flash", model_provider="google_genai")
        except Exception as e:
            _msg = f"Failed to initialize ChatOpenAI model: {e}"
            logger.error(_msg)
            raise Error(_msg) from e

    @staticmethod
    async def _setup_tools(_mcp_client: MultiServerMCPClient) -> list[BaseTool]:
        """
        Retrieve a list of tools from the provided MCP client.

        Args:
            _mcp_client: The MultiServerMCPClient instance used to fetch available tools.

        Returns:
            list[BaseTool]: A list of BaseTool objects retrieved from the MCP client.
        """
        try:
            return await _mcp_client.get_tools()
        except Exception as e:
            logger.warning(f"Failed to setup tools: {e}")
            logger.warning("Using empty tool list")
            return []

    @classmethod
    def draw_graph(cls) -> Path:
        """Render the compiled state graph as a Mermaid PNG image and save it."""
        cls._deep_agent.get_graph().draw_mermaid_png(
            output_file_path=cls.settings.directory.assets / "graph.png",
        )
        return cls.settings.directory.assets / "graph.png"

    @classmethod
    def gui(cls) -> Blocks:
        """
        Creates and returns the main Gradio Blocks interface for the Chattr app.

        Returns:
            Blocks: The constructed Gradio Blocks interface for the chat application.
        """
        with Blocks() as chat:
            with Sidebar(visible=cls.settings.debug):
                with Row():
                    with Column():
                        Markdown("# Chattr Graph")
                        Image(cls.draw_graph())
                with Row():
                    with Column():
                        Markdown("---")
                        Markdown("# Model Prompt")
                        Markdown(cls._setup_prompt())
            with Row():
                with Column():
                    video = Video(
                        label="Output Video",
                        interactive=False,
                        autoplay=True,
                        sources="upload",
                        format="mp4",
                    )
                    audio = Audio(
                        label="Output Audio",
                        interactive=False,
                        autoplay=True,
                        sources="upload",
                        type="filepath",
                        format="wav",
                    )
                with Column():
                    chatbot = Chatbot(
                        type="messages",
                        show_copy_button=True,
                        show_share_button=True,
                    )
                    msg = Textbox()
                    with Row():
                        button = Button("Send", variant="primary")
                        _ = ClearButton([msg, chatbot, video], variant="stop")
            _ = button.click(
                cls.generate_response,
                [msg, chatbot],
                [msg, chatbot, audio, video],
            )
            _ = msg.submit(
                cls.generate_response,
                [msg, chatbot],
                [msg, chatbot, audio, video],
            )
        return chat

    @classmethod
    async def generate_response(
        cls,
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
        is_audio_generated: bool = False
        audio_file: FilePath | None = None
        last_agent_message: AIMessage | None = None
        async for response in cls._deep_agent.astream(
            State(messages=[HumanMessage(content=message)], mem0_user_id="1"),
            RunnableConfig(configurable={"thread_id": "1"}),
            stream_mode="updates",
        ):
            logger.debug(f"Response type received: {response.keys()}")
            if response.keys() == {"agent"}:
                logger.debug(f"-------- Agent response {response}")
                last_agent_message: AIMessage = response["agent"]["messages"][-1]
                if last_agent_message.tool_calls:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(
                                last_agent_message.tool_calls[0]["args"],
                                indent=4,
                            ),
                            metadata=MetadataDict(
                                title=last_agent_message.tool_calls[0]["name"],
                                id=last_agent_message.tool_calls[0]["id"],
                            ),
                        ),
                    )
                else:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=last_agent_message.content,
                        ),
                    )
            elif response.keys() == {"tools"}:
                logger.debug(f"-------- Tool Message: {response}")
                last_tool_message: ToolMessage = response["tools"]["messages"][-1]
                history.append(
                    ChatMessage(
                        role="assistant",
                        content=last_tool_message.content,
                        metadata=MetadataDict(
                            title=last_tool_message.name,
                            id=last_tool_message.id,
                        ),
                    ),
                )
                if cls._is_url(last_tool_message.content):
                    logger.info(f"Downloading audio from {last_tool_message.content}")
                    file_path: Path = (
                        cls.settings.directory.audio / last_tool_message.id
                    )
                    audio_file = file_path.with_suffix(".wav")
                    cls._download_file(last_tool_message.content, audio_file)
                    logger.info(f"Audio downloaded to {audio_file}")
                    is_audio_generated = True
                    yield "", history, audio_file, None
            else:
                _msg = f"Unsupported audio source: {response.keys()}"
                logger.warning(_msg)
                raise Error(_msg)
            yield "", history, audio_file if is_audio_generated else None, None

    @classmethod
    def _is_url(cls, value: str | None) -> bool:
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
            return True
        except ValidationError:
            return False

    @classmethod
    def _download_file(cls, url: HttpUrl, path: Path) -> None:
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
