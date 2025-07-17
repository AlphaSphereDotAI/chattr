from typing import Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
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
    MODEL_API_KEY,
    MODEL_NAME,
    MODEL_TEMPERATURE,
    MODEL_URL,
    REDIS_URL,
)

SYSTEM_MESSAGE: SystemMessage = SystemMessage(
    content="You are a helpful assistant that can answer questions about the time and generate audio files from text."
)


async def setup_redis() -> AsyncRedisSaver:
    async with AsyncRedisSaver.from_conn_string(REDIS_URL) as checkpointer:
        await checkpointer.asetup()
        return checkpointer


async def create_graph() -> CompiledStateGraph:
    """
    Asynchronously creates and compiles a conversational state graph for a
    time-answering assistant with integrated external tools.

    Returns:
        CompiledStateGraph: The compiled state graph ready for execution, with nodes for agent responses and tool invocation.
    """
    # redis_saver: AsyncRedisSaver = await setup_redis()

    _mcp_servers_config: Dict[str, Dict[str, str | List[str]]] = {
        "qdrant_mcp": {
            "command": "uvx",
            "args": ["mcp-server-qdrant"],
            "transport": "stdio",
            "env": {
                "QDRANT_URL": "http://localhost:6333",
                "COLLECTION_NAME": "chattr",
            },
        },
        "time": {"command": "uvx", "args": ["mcp-server-time"], "transport": "stdio"},
        # "visualizr": {"url": MCP_VIDEO_GENERATOR, "transport": "sse"},
        # "vocalizr": {"url": MCP_VOICE_GENERATOR, "transport": "sse"}
    }
    _mcp_client: MultiServerMCPClient = MultiServerMCPClient(_mcp_servers_config)
    _tools: list[BaseTool] = await _mcp_client.get_tools()
    try:
        _llm: ChatOpenAI = ChatOpenAI(
            base_url=MODEL_URL,
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            temperature=MODEL_TEMPERATURE,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize ChatOpenAI model: {e}") from e

    _model: Runnable = _llm.bind_tools(_tools, parallel_tool_calls=False)

    async def _call_model(state: MessagesState) -> MessagesState:
        response = await _model.ainvoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": response}

    _graph_builder: StateGraph = StateGraph(MessagesState)
    _graph_builder.add_node("agent", _call_model)
    _graph_builder.add_node("tools", ToolNode(_tools))
    _graph_builder.add_edge(START, "agent")
    _graph_builder.add_conditional_edges("agent", tools_condition)
    _graph_builder.add_edge("tools", "agent")
    _graph: CompiledStateGraph = _graph_builder.compile(
        # checkpointer=redis_saver
        debug=True
    )

    return _graph


def draw_graph(graph: CompiledStateGraph) -> None:
    """
    Render the compiled state graph as a Mermaid PNG image and save it to the assets directory.
    """
    graph.get_graph().draw_mermaid_png(output_file_path=ASSETS_DIR / "graph.png")


if __name__ == "__main__":
    import asyncio

    async def test_graph():
        """
        Asynchronously creates and tests the conversational state graph by
        sending a time-related query and printing the resulting messages.
        """
        g: CompiledStateGraph = await create_graph()
        # draw_graph(g)

        for response in g.stream(
            {
                "messages": [
                    HumanMessage(content="What is the time? and store it in database")
                ]
            },
            {"configurable": {"thread_id": "1"}},
            stream_mode="updates",
        ):
            print(response)

    asyncio.run(test_graph())
