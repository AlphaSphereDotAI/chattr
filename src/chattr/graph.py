from typing import Literal

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from chattr import GROQ_MODEL_NAME, GROQ_MODEL_TEMPERATURE


class Graph:
    def __init__(self):
        self.tools = [self.get_weather]
        self.model = ChatGroq(model=GROQ_MODEL_NAME, temperature=GROQ_MODEL_TEMPERATURE)
        self.final_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.model = self.model.bind_tools(self.tools)
        self.final_model = self.final_model.with_config(tags=["final_node"])
        self._builder: StateGraph = StateGraph(MessagesState)
        self._builder.add_node("agent", self.call_model)
        self._builder.add_node("tools", ToolNode(self.tools))
        self._builder.add_node("final", self.call_final_model)
        self._builder.add_edge(START, "agent")
        self._builder.add_conditional_edges("agent", self.should_continue)
        self._builder.add_edge("tools", "agent")
        self._builder.add_edge("final", END)
        self.graph: CompiledStateGraph = self._builder.compile()

    def __repr__(self):
        return self.graph.get_graph().draw_ascii()

    def __call__(self, *args, **kwargs):
        return self.graph.invoke(*args, **kwargs)

    def should_continue(self, state: MessagesState) -> Literal["tools", "final"]:
        messages = state["messages"]
        last_message = messages[-1]
        # If the LLM makes a tool call, then we route to the "tools" node
        return "tools" if last_message.tool_calls else "final"

    def call_model(self, state: MessagesState) -> MessagesState:
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def call_final_model(self, state: MessagesState) -> MessagesState:
        messages = state["messages"]
        last_ai_message = messages[-1]
        response = self.final_model.invoke(
            [
                SystemMessage("Rewrite this in the voice of Al Roker"),
                HumanMessage(last_ai_message.content),
            ]
        )
        # overwrite the last AI message from the agent
        response.id = last_ai_message.id
        return {"messages": [response]}

    @tool
    def get_weather(self, city: Literal["nyc", "sf"]) -> str:
        """Use this to get weather information."""
        if city == "nyc":
            return "It might be cloudy in nyc"
        elif city == "sf":
            return "It's always sunny in sf"
        else:
            raise AssertionError("Unknown city")
