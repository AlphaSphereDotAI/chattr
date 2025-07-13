from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
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


async def create_graph() -> CompiledStateGraph:
    _mcp_client = MultiServerMCPClient(
        {
            "time": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/time"],
                "transport": "stdio",
            }
        }
    )
    _tools: list[BaseTool] = await _mcp_client.get_tools()
    _model: ChatOpenAI = ChatOpenAI(
        base_url=MODEL_URL,
        model=MODEL_NAME,
        api_key=MODEL_API_KEY,
        temperature=MODEL_TEMPERATURE,
    )
    _model = _model.bind_tools(_tools, parallel_tool_calls=False)

    def call_model(state: MessagesState) -> MessagesState:
        return {
            "messages": [_model.invoke([SYSTEM_MESSAGE] + state["messages"])]
        }

    _builder: StateGraph = StateGraph(MessagesState)
    _builder.add_node("agent", call_model)
    _builder.add_node("tools", ToolNode(_tools))
    _builder.add_edge(START, "agent")
    _builder.add_conditional_edges("agent", tools_condition)
    _builder.add_edge("tools", "agent")
    graph: CompiledStateGraph = _builder.compile()
    return graph


def draw_graph(graph: CompiledStateGraph) -> None:
    graph.get_graph().draw_mermaid_png(
        output_file_path=ASSETS_DIR / "graph.png"
    )


if __name__ == "__main__":
    import asyncio

    async def test_graph():
        g: CompiledStateGraph = await create_graph()

        messages = await g.ainvoke(
            {"messages": [HumanMessage(content="What is the time?")]}
        )

        for m in messages["messages"]:
            m.pretty_print()

    asyncio.run(test_graph())
