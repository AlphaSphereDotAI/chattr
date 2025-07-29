import json
from pathlib import Path
from gradio import (
    Blocks,
    Button,
    Chatbot,
    ChatMessage,
    ClearButton,
    Column,
    LikeData,
    PlayableVideo,
    Row,
    Textbox,
)
from gradio.components.chatbot import MetadataDict
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from chattr.graph.runner import graph


async def generate_response(message: str, history: list):
    graph_config: RunnableConfig = {"configurable": {"thread_id": "1"}}
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
        yield "", history, Path("./t.mp4")

def like(evt: LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)


def app_block() -> Blocks:
    with Blocks() as chat:
        with Row():
            with Column():
                video = PlayableVideo()
            with Column():
                chatbot = Chatbot(
                    type="messages", show_copy_button=True, show_share_button=True
                )
                msg = Textbox()
                with Row():
                    button = Button("Send", variant="primary")
                    ClearButton([msg, chatbot], variant="stop")
        chatbot.like(like)
        button.click(generate_response, [msg, chatbot], [msg, chatbot, video])
        msg.submit(generate_response, [msg, chatbot], [msg, chatbot, video])
    return chat
