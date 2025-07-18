import json

from gradio import Blocks, TabbedInterface, ChatMessage, ChatInterface
from gradio.components.chatbot import MetadataDict
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from chattr.graph import create_graph


async def generate_response(message, history):
    graph_config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    graph: CompiledStateGraph = await create_graph()
    async for response in graph.astream(
        {"messages": [HumanMessage(content=message)]},
        graph_config,
        stream_mode="updates",
    ):
        last_agent_message = response["agent"]["messages"][-1]
        if last_agent_message.tool_calls:
            # print(last_agent_message.tool_calls[0])
            return ChatMessage(
                role="assistant",
                content=json.dumps(last_agent_message.tool_calls[0]["args"]),
                metadata=MetadataDict(
                    title=last_agent_message.tool_calls[0]["name"],
                    id=last_agent_message.tool_calls[0]["id"],
                ),
            )
        else:
            # print(last_agent_message.content)
            return ChatMessage(role="assistant", content=last_agent_message.content)
    return None


def app_block() -> Blocks:
    """
    Constructs and returns the main Gradio chat application interface with a thread ID input, chatbot display, and control buttons.

    Returns:
        Blocks: The complete Gradio Blocks interface for the chat application.
    """

    chat = ChatInterface(generate_response, type="messages", save_history=True)
    return TabbedInterface([chat], ["Chattr"])
