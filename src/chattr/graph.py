from os import getenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from chattr import (
    ASSETS_DIR,
    MODEL_TEMPERATURE,
    MCP_VIDEO_GENERATOR,
    MCP_VOICE_GENERATOR,
    MODEL_URL,
    MODEL_NAME,
    MODEL_API_KEY,
)
from typing import Dict, List

SYSTEM_MESSAGE: SystemMessage = SystemMessage(
    content="You are a helpful assistant that can answer questions about the time and generate audio files from text."
)
DB_URI = "redis://localhost:6379"


async def setup_redis() -> AsyncRedisSaver:
    async with AsyncRedisSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.asetup()
        return checkpointer


async def create_graph() -> CompiledStateGraph:
    """
    Asynchronously creates and compiles a conversational state graph for a time-answering assistant with integrated external tools.

    Returns:
        CompiledStateGraph: The compiled state graph ready for execution, with nodes for agent responses and tool invocation.
    """
    # redis_saver: AsyncRedisSaver = await setup_redis()
    _vocalizr_mcp_servers_config: Dict[str, Dict[str, str | List[str]]] = {
        "vocalizr": {"url": MCP_VOICE_GENERATOR, "transport": "sse"}
    }
    _visualizr_mcp_servers_config: Dict[str, Dict[str, str | List[str]]] = {
        "visualizr": {"url": MCP_VIDEO_GENERATOR, "transport": "sse"}
    }
    _chattr_mcp_servers_config: Dict[str, Dict[str, str | List[str]]] = {
        "qdrant_mcp": {
            "command": "uvx",
            "args": ["mcp-server-qdrant"],
            "transport": "stdio",
            "env": {
                "QDRANT_URL": "http://localhost:6333",
                "COLLECTION_NAME": "chattr",
            },
        }
    }
    _vocalizr_mcp_client: MultiServerMCPClient = MultiServerMCPClient(
        _vocalizr_mcp_servers_config
    )
    _visualizr_mcp_client: MultiServerMCPClient = MultiServerMCPClient(
        _visualizr_mcp_servers_config
    )
    _chattr_mcp_client: MultiServerMCPClient = MultiServerMCPClient(
        _chattr_mcp_servers_config
    )
    _vocalizr_tools: list[BaseTool] = await _vocalizr_mcp_client.get_tools()
    _visualizr_tools: list[BaseTool] = await _visualizr_mcp_client.get_tools()
    _chattr_tools: list[BaseTool] = await _chattr_mcp_client.get_tools()
    try:
        _model: ChatOpenAI = ChatOpenAI(
            base_url=MODEL_URL,
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            temperature=MODEL_TEMPERATURE,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize ChatOpenAI model: {e}") from e

    _vocalizr_model = _model.bind_tools(
        _vocalizr_tools,
        parallel_tool_calls=False,
    )
    _visualizr_model = _model.bind_tools(
        _visualizr_tools,
        parallel_tool_calls=False,
    )
    _chattr_model = _model.bind_tools(
        _chattr_tools,
        parallel_tool_calls=False,
    )

    async def _vocalizr_call_model(state: MessagesState) -> MessagesState:
        response = await _vocalizr_model.ainvoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": response}

    async def _visualizr_call_model(state: MessagesState) -> MessagesState:
        response = await _visualizr_model.ainvoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": response}

    async def _chattr_call_model(state: MessagesState) -> MessagesState:
        response = await _chattr_model.ainvoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": response}

    _vocalizr_graph_builder: StateGraph = StateGraph(MessagesState)
    _vocalizr_graph_builder.add_node("agent", _vocalizr_call_model)
    _vocalizr_graph_builder.add_node("tools", ToolNode(_vocalizr_tools))
    _vocalizr_graph_builder.add_edge(START, "agent")
    _vocalizr_graph_builder.add_conditional_edges("agent", tools_condition)
    _vocalizr_graph_builder.add_edge("tools", "agent")
    _vocalizr_graph: CompiledStateGraph = _vocalizr_graph_builder.compile(
        # checkpointer=redis_saver
        debug=True,
        name="vocalizr",
    )

    _visualizr_graph_builder: StateGraph = StateGraph(MessagesState)
    _visualizr_graph_builder.add_node("agent", _visualizr_call_model)
    _visualizr_graph_builder.add_node("tools", ToolNode(_visualizr_tools))
    _visualizr_graph_builder.add_edge(START, "agent")
    _visualizr_graph_builder.add_conditional_edges("agent", tools_condition)
    _visualizr_graph_builder.add_edge("tools", "agent")
    _visualizr_graph: CompiledStateGraph = _visualizr_graph_builder.compile(
        # checkpointer=redis_saver
        debug=True,
        name="visualizr",
    )

    _chattr_graph_builder: StateGraph = StateGraph(MessagesState)
    _chattr_graph_builder.add_node("agent", _chattr_call_model)
    _chattr_graph_builder.add_node("vocalizr", _vocalizr_graph)
    _chattr_graph_builder.add_node("visualizr", _visualizr_graph)
    _chattr_graph_builder.add_edge(START, "agent")

    _chattr_graph_builder.add_conditional_edges("agent", tools_condition)
    _chattr_graph_builder.add_edge("tools", "agent")
    _chattr_graph: CompiledStateGraph = _chattr_graph_builder.compile(
        # checkpointer=redis_saver
        debug=True,
        name="chattr",
    )

    return _chattr_graph


def draw_graph(graph: CompiledStateGraph) -> None:
    """
    Render the compiled state graph as a Mermaid PNG image and save it to the assets directory.
    """
    graph.get_graph().draw_mermaid_png(output_file_path=ASSETS_DIR / "graph.png")


if __name__ == "__main__":
    import asyncio

    async def test_graph():
        """
        Asynchronously creates and tests the conversational state graph by sending a time-related query and printing the resulting messages.
        """
        g: CompiledStateGraph = await create_graph()

        messages = await g.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content="What is the time? and generate an audio file from the answer."
                    )
                ]
            }
        )

        for m in messages["messages"]:
            m.pretty_print()

    asyncio.run(test_graph())
