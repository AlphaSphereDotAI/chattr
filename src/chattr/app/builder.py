"""Main orchestration graph for the Chattr application."""

from collections.abc import AsyncGenerator
from json import dumps, loads
from pathlib import Path
from textwrap import dedent
from typing import AsyncGenerator, Self

from gradio import ChatMessage
from gradio.components.chatbot import MetadataDict
from m3u8 import M3U8, load
from poml import poml
from pydantic import HttpUrl, ValidationError
from requests import Session
from rich.pretty import pprint

from chattr.app.settings import Settings, logger


class App:
    """Main application class for the Chattr Multi-agent system app."""

    settings: Settings

    def __init__(self, memory: Memory, tools: list[BaseTool]):
        self._memory: Memory = memory
        self._tools: list[BaseTool] = tools
        self._llm: ChatOpenAI = self._initialize_llm()
        self._model: Runnable = self._llm.bind_tools(self._tools)
        self._graph: CompiledStateGraph = self._build_state_graph()

    @classmethod
    async def create(cls, settings: Settings) -> Self:
        """Async factory method to create a Graph instance."""
        cls.settings = settings
        tools = []
        memory = await cls._setup_memory()
        try:
            tools: list[BaseTool] = await cls._setup_tools(
                MultiServerMCPClient(
                    loads(cls.settings.mcp.path.read_text(encoding="utf-8"))
                )
            )
        except Exception as e:
            logger.warning(f"Failed to setup tools: {e}")
        return cls(memory, tools)

    def _build_state_graph(self) -> CompiledStateGraph:
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
            messages = state.get("messages")
            user_id = state.get("mem0_user_id")
            if not user_id:
                logger.warning("No user_id found in state")
                user_id = "default"
            memories = self._memory.search(messages[-1].content, user_id=user_id)
            if memories:
                memory_list = "\n".join(
                    [f"- {memory.get('memory')}" for memory in memories]
                )
                context = dedent(
                    f"""
                    Relevant information from previous conversations:
                    {memory_list}
                    """
                )
            else:
                context = "No previous conversation history available."
            logger.debug(f"Memory context: {context}")
            system_message: SystemMessage = SystemMessage(
                content=dedent(
                    f"""
                    {self.settings.model.system_message}
                    Use the provided context to personalize your responses and
                    remember user preferences and past interactions.
                    {context}
                    """
                )
            )
            response = await self._model.ainvoke([system_message] + messages)
            self._memory.add(
                f"User: {messages[-1].content}\nAssistant: {response.content}",
                user_id=user_id,
            )
            return State(messages=[response], mem0_user_id=user_id)

        graph_builder: StateGraph = StateGraph(State)
        graph_builder.add_node("agent", _call_model)
        graph_builder.add_node("tools", ToolNode(self._tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        return graph_builder.compile(debug=True)

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
            logger.error(f"Failed to initialize ChatOpenAI model: {e}")
            raise

    @classmethod
    async def _setup_memory(cls) -> Memory:
        """
        Initialize and set up the store and checkpointer for state persistence.

        Returns:
            Memory: Configured memory instances.
        """
        return Memory.from_config(
            {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "host": cls.settings.vector_database.url.host,
                        "port": cls.settings.vector_database.url.port,
                        "collection_name": cls.settings.memory.collection_name,
                        "embedding_model_dims": cls.settings.memory.embedding_dims,
                    },
                },
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": cls.settings.model.name,
                        "openai_base_url": str(cls.settings.model.url),
                        "api_key": cls.settings.model.api_key,
                    },
                },
                "embedder": {
                    "provider": "langchain",
                    "config": {"model": FastEmbedEmbeddings()},
                },
            }
        )

    @staticmethod
    async def _setup_tools(_mcp_client: MultiServerMCPClient) -> list[BaseTool]:
        """
        Create and return the main Gradio Blocks interface for the Chattr app.

        Returns:
            Blocks: The constructed Gradio Blocks interface for the chat application.
        """
        try:
            return await _mcp_client.get_tools()
        except Exception as e:
            logger.warning(f"Failed to setup tools: {e}")
            logger.warning("Using empty tool list")
            return []

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
                            content=dumps(
                                last_agent_message.tool_calls[0]["args"], indent=4
                            ),
                            metadata=MetadataDict(
                                title=response.tool.tool_name,
                                id=response.tool.tool_call_id,
                                duration=response.tool.created_at,
                            ),
                        ),
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
