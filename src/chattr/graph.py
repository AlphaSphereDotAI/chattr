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
    MODEL_API_KEY,
    MODEL_NAME,
    MODEL_TEMPERATURE,
    MODEL_URL,
)

SYSTEM_MESSAGE: SystemMessage = SystemMessage(
    content="You are a helpful assistant that can answer questions about the time."
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
    redis_saver: AsyncRedisSaver = await setup_redis()
    _mcp_servers_config: dict[str, dict[str, str | list[str]]] = {
        "time": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "mcp/time"],
            "transport": "stdio",
        }
    }
    _mcp_client: MultiServerMCPClient = MultiServerMCPClient(
        _mcp_servers_config
    )
    _tools: list[BaseTool] = await _mcp_client.get_tools()
    try:
        _model: ChatOpenAI = ChatOpenAI(
            base_url=MODEL_URL,
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            temperature=MODEL_TEMPERATURE,
        )
        _model = _model.bind_tools(_tools, parallel_tool_calls=False)
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize ChatOpenAI model: {e}"
        ) from e

    async def call_model(state: MessagesState) -> MessagesState:
        response = await _model.ainvoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": response}

    _builder: StateGraph = StateGraph(MessagesState)
    _builder.add_node("agent", call_model)
    _builder.add_node("tools", ToolNode(_tools))
    _builder.add_edge(START, "agent")
    _builder.add_conditional_edges("agent", tools_condition)
    _builder.add_edge("tools", "agent")
    graph: CompiledStateGraph = _builder.compile(checkpointer=redis_saver)
    return graph


def draw_graph(graph: CompiledStateGraph) -> None:
    """
    Render the compiled state graph as a Mermaid PNG image and save it to the assets directory.
    """
    graph.get_graph().draw_mermaid_png(
        output_file_path=ASSETS_DIR / "graph.png"
    )


if __name__ == "__main__":
    import asyncio

    async def test_graph():
        """
        Asynchronously creates and tests the conversational state graph by sending a time-related query and printing the resulting messages.
        """
        g: CompiledStateGraph = await create_graph()

        messages = await g.ainvoke(
            {"messages": [HumanMessage(content="What is the time?")]}
        )

        for m in messages["messages"]:
            m.pretty_print()

    asyncio.run(test_graph())
