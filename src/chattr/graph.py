from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool, tool
from langchain_groq import ChatGroq
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from chattr import ASSETS_DIR, GROQ_MODEL_NAME, GROQ_MODEL_TEMPERATURE


class Graph:
    def __init__(self):
        self.system_message: SystemMessage = SystemMessage(
            content="You are a helpful assistant that can answer questions about the weather."
        )
        self.tools: list[BaseTool] = [self.get_weather]
        self.model: ChatGroq = ChatGroq(
            model=GROQ_MODEL_NAME, temperature=GROQ_MODEL_TEMPERATURE
        )
        self.model = self.model.bind_tools(self.tools, parallel_tool_calls=False)
        self._builder: StateGraph = StateGraph(MessagesState)
        self._builder.add_node("agent", self.call_model)
        self._builder.add_node("tools", ToolNode(self.tools))
        self._builder.add_edge(START, "agent")
        self._builder.add_conditional_edges("agent", tools_condition)
        self._builder.add_edge("tools", "agent")
        self.graph: CompiledStateGraph = self._builder.compile()

    def draw(self):
        self.graph.get_graph().draw_mermaid_png(
            output_file_path=ASSETS_DIR / "graph.png"
        )

    def __call__(self, *args, **kwargs):
        return self.graph.invoke(*args, **kwargs)

    def call_model(self, state: MessagesState) -> MessagesState:
        return {
            "messages": [self.model.invoke([self.system_message] + state["messages"])]
        }

    @tool
    def get_weather(self, city: Literal["nyc", "sf"]) -> str:
        """Use this to get weather information."""
        if city == "nyc":
            return "It might be cloudy in nyc"
        elif city == "sf":
            return "It's always sunny in sf"
        else:
            raise AssertionError("Unknown city")


if __name__ == "__main__":
    Graph().draw()
