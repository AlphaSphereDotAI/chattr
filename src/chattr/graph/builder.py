import json
from logging import getLogger
from pathlib import Path

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

from chattr.settings import Settings
from chattr.utils import download, is_url

logger = getLogger(__name__)
from asyncio import run


class Graph:
    def __init__(self, settings: Settings):
        self.settings: Settings = settings
        self.system_message: SystemMessage = SystemMessage(
            content="You are a helpful assistant that can answer questions about the time and generate audio files from text."
        )
        # redis_saver: AsyncRedisSaver = await self.setup_redis()
        self._mcp_servers_config: dict[
            str,
            StdioConnection
            | SSEConnection
            | StreamableHttpConnection
            | WebsocketConnection,
        ] = {
            "vector_database": StdioConnection(
                command="uvx",
                args=["mcp-server-qdrant"],
                env={
                    "QDRANT_URL": "http://localhost:6333",
                    "COLLECTION_NAME": "chattr",
                },
                transport="stdio",
            ),
            "time": StdioConnection(
                command="uvx",
                args=["mcp-server-time"],
                transport="stdio",
            ),
            # self.settings.video_generator_mcp.name: {
            #     "url": str(self.settings.video_generator_mcp.url),
            #     "transport": self.settings.video_generator_mcp.transport,
            # },
            self.settings.voice_generator_mcp.name: {
                "url": str(self.settings.voice_generator_mcp.url),
                "transport": self.settings.voice_generator_mcp.transport,
            },
        }
        self._tools: list[BaseTool] = run(
            self._setup_tools(MultiServerMCPClient(self._mcp_servers_config))
        )
        try:
            self._llm: ChatOpenAI = ChatOpenAI(
                base_url=str(self.settings.model.url),
                model=self.settings.model.name,
                api_key=self.settings.model.api_key,
                temperature=self.settings.model.temperature,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI model: {e}")
            raise
        self._model: Runnable = self._llm.bind_tools(
            self._tools, parallel_tool_calls=False
        )

        async def _call_model(state: MessagesState) -> MessagesState:
            response = await self._model.ainvoke(
                [self.system_message] + state["messages"]
            )
            return {"messages": [response]}

        self._graph_builder: StateGraph = StateGraph(MessagesState)
        self._graph_builder.add_node("agent", _call_model)
        self._graph_builder.add_node("tools", ToolNode(self._tools))
        self._graph_builder.add_edge(START, "agent")
        self._graph_builder.add_conditional_edges("agent", tools_condition)
        self._graph_builder.add_edge("tools", "agent")
        self._graph: CompiledStateGraph = self._graph_builder.compile(
            # checkpointer=redis_saver
            debug=True
        )

    async def _setup_redis(self) -> AsyncRedisSaver:
        async with AsyncRedisSaver.from_conn_string(
            self.settings.short_term_memory.url
        ) as checkpointer:
            await checkpointer.asetup()
            return checkpointer

    @staticmethod
    async def _setup_tools(_mcp_client: MultiServerMCPClient) -> list[BaseTool]:
        return await _mcp_client.get_tools()

    def draw_graph(self) -> None:
        """Render the compiled state graph as a Mermaid PNG image and save it."""
        self._graph.get_graph().draw_mermaid_png(
            output_file_path=self.settings.assets_dir / "graph.png"
        )

    def get_graph(self) -> CompiledStateGraph:
        return self._graph

    async def generate_response(self, message: str, history: list):
        graph_config: RunnableConfig = RunnableConfig(configurable={"thread_id": "1"})
        async for response in self._graph.astream(
            {"messages": [HumanMessage(content=message)]},
            graph_config,
            stream_mode="updates",
        ):
            if response.keys() == {"agent"}:
                last_agent_message = response["agent"]["messages"][-1]
                if last_agent_message.tool_calls:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=json.dumps(
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
                    download(
                        last_tool_message.content,
                        Path(
                            self.settings.directory.audio
                            / f"{last_tool_message.id}.wav"
                        ),
                    )
                    yield (
                        "",
                        history,
                        Path(
                            self.settings.directory.audio
                            / f"{last_tool_message.id}.wav"
                        ),
                    )
            yield "", history, Path()


if __name__ == "__main__":
    import asyncio

    async def test_graph():
        """
        Asynchronously creates and tests the conversational state graph by
        sending a time-related query and printing the resulting messages.
        """
        g: CompiledStateGraph = Graph()
        # draw_graph(g)

        async for response in g.astream(
            {
                "messages": [
                    HumanMessage(content="What is the time? and store it in database")
                ]
            },
            {"configurable": {"thread_id": "1"}},
            stream_mode="updates",
        ):
            # print(response)
            if response.keys() == {"agent"}:
                print("Tool call detected:", response["agent"]["messages"])
                print("Tool call detected len:", len(response["agent"]["messages"]))
                print("Tool call detected last:", response["agent"]["messages"][-1])
                if response["agent"]["messages"][-1].tool_calls:
                    print(response["agent"]["messages"][-1].tool_calls[0])
                else:
                    print(response["agent"]["messages"][-1].content)
            else:
                print("Tool call detected:", response["tools"]["messages"])
                print("Tool call detected len:", len(response["tools"]["messages"]))
                print("Tool call detected last:", response["tools"]["messages"][-1])
            print("=" * 20)

    asyncio.run(test_graph())
