"""This module contains the Graph class, which represents the main orchestration graph for the Chattr application."""

from json import dumps
from logging import getLogger
from pathlib import Path
from typing import AsyncGenerator, Self

from gradio import ChatMessage
from gradio.components.chatbot import MetadataDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import (
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
    WebsocketConnection,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.redis.aio import AsyncRedisStore

from chattr.settings import Settings
from chattr.utils import convert_audio_to_wav, download_file, is_url

logger = getLogger(__name__)


class Graph:
    """
    Represents the main orchestration graph for the Chattr application.
    This class manages the setup and execution of the conversational agent, tools, and state graph.

    Args:
        settings: The application settings used to configure the graph and its components.
    """

    def __init__(
        self,
        settings: Settings,
        store: AsyncRedisStore,
        saver: AsyncRedisSaver,
        mcp_client: MultiServerMCPClient,
        tools: list[BaseTool],
    ):
        self.settings: Settings = settings
        self.system_message: SystemMessage = SystemMessage(
            content="You are a helpful assistant that can answer questions about the time and generate audio files from text."
        )
        self._long_term_memory: AsyncRedisStore = store
        self._short_term_memory: AsyncRedisSaver = saver
        self._mcp_client: MultiServerMCPClient = mcp_client
        self._tools: list[BaseTool] = tools
        self._llm: ChatOpenAI = self._initialize_llm()
        self._model: Runnable = self._llm.bind_tools(self._tools)
        self._graph: CompiledStateGraph = self._build_state_graph()

    @classmethod
    async def create(cls, settings: Settings) -> Self:
        """Async factory method to create a Graph instance."""
        store, saver = await cls._setup_memory(settings)
        mcp_client: MultiServerMCPClient = MultiServerMCPClient(
            cls._create_mcp_config(settings)
        )
        tools: list[BaseTool] = await cls._setup_tools(mcp_client)
        return cls(settings, store, saver, mcp_client, tools)

    def _build_state_graph(self) -> CompiledStateGraph:
        """
        Construct and compile the state graph for the Chattr application.
        This method defines the nodes and edges for the conversational agent and tool interactions.

        Returns:
            CompiledStateGraph: The compiled state graph is ready for execution.
        """

        async def _call_model(state: MessagesState) -> MessagesState:
            response = await self._model.ainvoke(
                [self.system_message] + state["messages"]
            )
            return MessagesState(messages=[response])

        graph_builder: StateGraph = StateGraph(MessagesState)
        graph_builder.add_node("agent", _call_model)
        graph_builder.add_node("tools", ToolNode(self._tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        return graph_builder.compile(
            debug=True,
            checkpointer=self._short_term_memory,
            store=self._long_term_memory,
        )

    def _create_mcp_config(
        self,
    ) -> dict[
        str,
        StdioConnection
        | SSEConnection
        | StreamableHttpConnection
        | WebsocketConnection,
    ]:
        """
        Create the configuration dictionary for MCP (Multi-Component Protocol) servers.
        This method sets up the connection details for each MCP server used by the application.

        Returns:
            dict: A dictionary mapping server names to their connection configurations.
        """

        return {
            "vector_database": StdioConnection(
                command="uvx",
                args=["mcp-server-qdrant"],
                env={
                    "QDRANT_URL": str(self.settings.vector_database.url),
                    "COLLECTION_NAME": self.settings.vector_database.name,
                },
                transport="stdio",
            ),
            "time": StdioConnection(
                command="uvx",
                args=["mcp-server-time"],
                transport="stdio",
            ),
            self.settings.voice_generator_mcp.name: SSEConnection(
                url=str(self.settings.voice_generator_mcp.url),
                transport=self.settings.voice_generator_mcp.transport,
            ),
        }

    def _initialize_llm(self) -> ChatOpenAI:
        """
        Initialize the ChatOpenAI language model using the provided settings.
        This method creates and returns a ChatOpenAI instance configured with the model's URL, name, API key, and temperature.

        Returns:
            ChatOpenAI: The initialized ChatOpenAI language model instance.

        Raises:
            Exception: If the model initialization fails.
        """
        try:
            return ChatOpenAI(
                base_url=str(self.settings.model.url),
                model=self.settings.model.name,
                api_key=self.settings.model.api_key,
                temperature=self.settings.model.temperature,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI model: {e}")
            raise

    async def _setup_memory(self) -> tuple[AsyncRedisStore, AsyncRedisSaver]:
        """
        Initialize and set up the Redis store and checkpointer for state persistence.

        Returns:
            tuple[AsyncRedisStore, AsyncRedisSaver]: Configured Redis store and saver instances.
        """
        store_ctx = AsyncRedisStore.from_conn_string(str(self.settings.memory.url))
        store = await store_ctx.__aenter__()
        checkpointer_ctx = AsyncRedisSaver.from_conn_string(
            str(self.settings.memory.url)
        )
        checkpointer = await checkpointer_ctx.__aenter__()
        await store.setup()
        await checkpointer.asetup()
        return store, checkpointer

    @staticmethod
    async def _setup_tools(_mcp_client: MultiServerMCPClient) -> list[BaseTool]:
        """
        Retrieve a list of tools from the provided MCP client.

        Args:
            _mcp_client: The MultiServerMCPClient instance used to fetch available tools.

        Returns:
            list[BaseTool]: A list of BaseTool objects retrieved from the MCP client.
        """
        return await _mcp_client.get_tools()

    def draw_graph(self) -> None:
        """Render the compiled state graph as a Mermaid PNG image and save it."""
        self._graph.get_graph().draw_mermaid_png(
            output_file_path=self.settings.directory.assets / "graph.png"
        )

    async def generate_response(
        self, message: str, history: list[ChatMessage]
    ) -> AsyncGenerator[tuple[str, list[ChatMessage], Path | None]]:
        """
        Generate a response to a user message and update the conversation history.
        This asynchronous method streams responses from the state graph and yields updated history and audio file paths as needed.

        Args:
            message: The user's input message as a string.
            history: The conversation history as a list of ChatMessage objects.

        Returns:
            AsyncGenerator[tuple[str, list[ChatMessage], Path]]: Yields a tuple containing an empty string, the updated history, and a Path to an audio file if generated.
        """
        graph_config: RunnableConfig = RunnableConfig(
            configurable={"thread_id": "1", "user_id": "1"}
        )
        async for response in self._graph.astream(
            MessagesState(messages=[HumanMessage(content=message)]),
            graph_config,
            stream_mode="updates",
        ):
            if response.keys() == {"agent"}:
                last_agent_message = response["agent"]["messages"][-1]
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
            else:
                last_tool_message = response["tools"]["messages"][-1]
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
                if is_url(last_tool_message.content):
                    logger.info(f"Downloading audio from {last_tool_message.content}")
                    file_path: Path = (
                        self.settings.directory.audio / last_tool_message.id
                    )
                    download_file(
                        last_tool_message.content, file_path.with_suffix(".aac")
                    )
                    logger.info(f"Audio downloaded to {file_path.with_suffix('.aac')}")
                    convert_audio_to_wav(
                        file_path.with_suffix(".aac"), file_path.with_suffix(".wav")
                    )
                    yield "", history, file_path.with_suffix(".wav")
            yield "", history, None
