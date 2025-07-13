from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from chattr import ASSETS_DIR
from chattr.tools import get_weather

SYSTEM_MESSAGE: SystemMessage = SystemMessage(
    content="You are a helpful assistant that can answer questions about the weather."
)


def create_graph() -> CompiledStateGraph:
    _model: ChatOpenAI = ChatOpenAI(
        base_url="http://127.0.0.1:12434/engines/v1",
        model="ai/qwen3:0.6B-Q4_0",
        api_key="not-needed",
        temperature=0.0,
    )
    _tools: List[BaseTool] = [get_weather]
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
    g = create_graph()

    messages = g.invoke(
        {"messages": [HumanMessage(content="What is the weather in sf?")]}
    )

    for m in messages["messages"]:
        m.pretty_print()
