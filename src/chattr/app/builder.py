"""Main orchestration graph for the Chattr application."""

from json import dumps, loads
from pathlib import Path
from textwrap import dedent
from typing import AsyncGenerator, Self

from gradio import (
    Audio,
    Blocks,
    Button,
    Chatbot,
    ChatMessage,
    ClearButton,
    Column,
    Error,
    Row,
    Textbox,
    Video,
)
from gradio.components.chatbot import MetadataDict
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from m3u8 import M3U8, load
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.llms.configs import LlmConfig
from mem0.vector_stores.configs import VectorStoreConfig
from openai import OpenAIError
from pydantic import FilePath, HttpUrl, ValidationError
from qdrant_client.http.exceptions import ResponseHandlingException
from requests import Session

from chattr.app.settings import Settings, logger
from chattr.app.state import State


class App:
    """Main application class for the Chattr Multi-agent system app."""

    settings: Settings
    _llm: ChatOpenAI
    _model: Runnable
    _tools: list[BaseTool]
    _memory: Memory
    _graph: CompiledStateGraph

    @classmethod
    async def create(cls, settings: Settings) -> Self:
        """Async factory method to create a Graph instance."""
        cls.settings = settings
        cls._tools = []
        try:
            mcp_config: dict[str, Connection] = loads(
                cls.settings.mcp.path.read_text(encoding="utf-8")
            )
            cls._tools = await cls._setup_tools(MultiServerMCPClient(mcp_config))
        except OSError as e:
            logger.warning(f"Failed to read MCP config file: {e}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse MCP config JSON: {e}")
        except Exception as e:
            logger.warning(f"Failed to setup MCP tools: {e}")
        cls._llm = cls._setup_llm()
        cls._model = cls._llm.bind_tools(cls._tools)
        cls._memory = await cls._setup_memory()
        cls._graph = cls._setup_graph()
        return cls()

    @classmethod
    def _setup_graph(cls) -> CompiledStateGraph:
        """
        Construct and compile the state graph for the Chattr application.
        This method defines the nodes and edges for the conversational agent
        and tool interactions.

        Returns:
            CompiledStateGraph: The compiled state graph is ready for execution.
        """

        async def _call_model(state: State) -> State:
            """
            Generate a model response based on the current state and user memory.
            This asynchronous function retrieves relevant memories,
            constructs a system message, and invokes the language model.

            Args:
                state: The current State object containing messages and user ID.

            Returns:
                State: The updated State object with the model's response message.
            """
            messages = state["messages"]
            user_id = state["mem0_user_id"]

            try:
                if not user_id:
                    logger.warning("No user_id found in state")
                    user_id = "default"
                memories = cls._memory.search(messages[-1].content, user_id=user_id)
                memory_list = memories["results"]
                logger.info(f"Retrieved {len(memory_list)} relevant memories")
                logger.debug(f"Memories: {memories}")

                if memory_list:
                    memory_list = "\n".join(
                        [f"- {memory.get('memory')}" for memory in memory_list]
                    )
                    context = dedent(
                        f"""
                        Relevant information from previous conversations:
                        {memory_list}
                        """
                    )
                else:
                    context = "No previous conversation history available."
                logger.debug(f"Memory context:\n{context}")
                system_message: SystemMessage = SystemMessage(
                    content=dedent(
                        f"""
                        {cls.settings.model.system_message}
                        Use the provided context to personalize your responses and
                        remember user preferences and past interactions.
                        {context}
                        """
                    )
                )
                response = await cls._model.ainvoke([system_message] + messages)
                try:
                    interaction = [
                        {"role": "user", "content": messages[-1].content},
                        {"role": "assistant", "content": response.content},
                    ]
                    mem0_result = cls._memory.add(interaction, user_id=user_id)
                    logger.info(f"Memory saved: {len(mem0_result.get('results', []))}")
                except Exception as e:
                    logger.exception(f"Error saving memory: {e}")
            except Exception as e:
                logger.error(f"Error in chatbot: {e}")
                # Fallback response without memory context
                response = await cls._model.ainvoke(
                    [cls.settings.model.system_message] + messages
                )
            return State(messages=[response], mem0_user_id=user_id)

        graph_builder: StateGraph = StateGraph(State)
        graph_builder.add_node("agent", _call_model)
        graph_builder.add_node("tools", ToolNode(cls._tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        return graph_builder.compile(debug=True)

    @classmethod
    def _setup_llm(cls) -> ChatOpenAI:
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
            return ChatOpenAI(
                base_url=str(cls.settings.model.url),
                model=cls.settings.model.name,
                api_key=cls.settings.model.api_key,
                temperature=cls.settings.model.temperature,
            )
        except Exception as e:
            _msg = f"Failed to initialize ChatOpenAI model: {e}"
            logger.error(_msg)
            raise Error(_msg) from e

    @classmethod
    async def _setup_memory(cls) -> Memory:
        """
        Initialize and set up the Memory for state persistence.

        Returns:
            Memory: Configured memory instances.
        """
        try:
            return Memory(
                MemoryConfig(
                    vector_store=VectorStoreConfig(
                        provider="qdrant",
                        config={
                            "host": cls.settings.vector_database.url.host,
                            "port": cls.settings.vector_database.url.port,
                            "collection_name": cls.settings.memory.collection_name,
                            "embedding_model_dims": cls.settings.memory.embedding_dims,
                        },
                    ),
                    llm=LlmConfig(
                        provider="langchain",
                        config={"model": cls._llm},
                    ),
                    embedder=EmbedderConfig(
                        provider="langchain",
                        config={"model": FastEmbedEmbeddings()},
                    ),
                )
            )
        except ResponseHandlingException as e:
            _msg = f"Failed to connect to Qdrant server: {e}"
            logger.error(_msg)
            raise Error(_msg) from e
        except OpenAIError as e:
            _msg = (
                "Failed to connect to Chat Model server: "
                "setting the `MODEL__API_KEY` environment variable"
            )
            logger.error(_msg)
            raise Error(_msg) from e
        except ValueError as e:
            _msg = f"Failed to initialize memory: {e}"
            logger.exception(_msg)
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
    def draw_graph(cls) -> None:
        """Render the compiled state graph as a Mermaid PNG image and save it."""
        cls._graph.get_graph().draw_mermaid_png(
            output_file_path=cls.settings.directory.assets / "graph.png"
        )

    @classmethod
    def gui(cls) -> Blocks:
        """Creates and returns the main Gradio Blocks interface for the Chattr app.

        This function sets up the user interface, including video, audio, chatbot, and input controls.

        Returns:
            Blocks: The constructed Gradio Blocks interface for the chat application.
        """
        with Blocks() as chat:
            with Row():
                with Column():
                    video = Video(
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
                        ClearButton([msg, chatbot, video], variant="stop")
            button.click(cls.generate_response, [msg, chatbot], [msg, chatbot, audio])
            msg.submit(cls.generate_response, [msg, chatbot], [msg, chatbot, audio])
        return chat

    @classmethod
    async def generate_response(
        cls, message: str, history: list[ChatMessage]
    ) -> AsyncGenerator[tuple[str, list[ChatMessage], Path | None]]:
        """
        Generate a response to a user message and update the conversation history.
        This asynchronous method streams responses from the state graph and yields updated history and audio file paths as needed.

        Args:
            message: The user's input message as a string.
            history: The conversation history as a list of ChatMessage objects.

        Returns:
            AsyncGenerator[tuple[str, list[ChatMessage], Path | None]]: Yields a tuple containing an empty string, the updated history, and a Path to an audio file if generated.
        """
        is_audio_generated: bool = False
        audio_file: FilePath | None = None
        last_agent_message: AnyMessage | None = None
        async for response in cls._graph.astream(
            State(messages=[HumanMessage(content=message)], mem0_user_id="1"),
            stream_mode="updates",
        ):
            if response.keys() == {"agent"}:
                last_agent_message: AIMessage = response["agent"]["messages"][-1]
                if last_agent_message.tool_calls:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(
                                last_agent_message.tool_calls[0]["args"], indent=4
                            ),
                            metadata=MetadataDict(
                                title=last_agent_message.tool_calls[0]["name"],
                                id=last_agent_message.tool_calls[0]["id"],
                            ),
                        )
                    )
                else:
                    history.append(
                        ChatMessage(
                            role="assistant", content=last_agent_message.content
                        )
                    )
            elif response.keys() == {"tools"}:
                last_tool_message: ToolMessage = response["tools"]["messages"][-1]
                history.append(
                    ChatMessage(
                        role="assistant",
                        content=last_tool_message.content,
                        metadata=MetadataDict(
                            title=last_tool_message.name,
                            id=last_tool_message.id,
                        ),
                    )
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
                    yield "", history, audio_file
            else:
                _msg = f"Unsupported audio source: {response.keys()}"
                logger.warning(_msg)
                raise Error(_msg)
            yield "", history, audio_file if is_audio_generated else None

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
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"File downloaded to {path}")
