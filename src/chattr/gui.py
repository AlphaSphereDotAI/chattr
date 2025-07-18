import json

from gradio import Blocks, TabbedInterface, ChatMessage, ChatInterface
from gradio.components.chatbot import MetadataDict
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from chattr.graph import create_graph


async def generate_response(message: str, history: list):
    graph_config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    graph: CompiledStateGraph = await create_graph()
    async for response in graph.astream(
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
                    ChatMessage(role="assistant", content=last_agent_message.content)
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
        yield history


def app_block() -> Blocks:
    chat = ChatInterface(generate_response, type="messages", save_history=True)
    return TabbedInterface([chat], ["Chattr"])
