from gradio import (
    Audio,
    Blocks,
    Button,
    Chatbot,
    ClearButton,
    Column,
    LikeData,
    PlayableVideo,
    Row,
    Textbox,
)

from chattr.graph.runner import graph


def like(evt: LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)


def app_block() -> Blocks:
    with Blocks() as chat:
        with Row():
            with Column():
                video = PlayableVideo()
                audio = Audio(sources="upload", type="filepath")
            with Column():
                chatbot = Chatbot(
                    type="messages",
                    show_copy_button=True,
                    show_share_button=True,
                )
                msg = Textbox()
                with Row():
                    button = Button("Send", variant="primary")
                    ClearButton([msg, chatbot], variant="stop")
        chatbot.like(like)
        button.click(graph.generate_response, [msg, chatbot], [msg, chatbot, audio])
        msg.submit(graph.generate_response, [msg, chatbot], [msg, chatbot, audio])
    return chat
