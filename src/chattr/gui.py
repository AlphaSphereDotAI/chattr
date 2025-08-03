"""This module contains the Gradio-based GUI for the Chattr app."""

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
    # TODO: Implement feedback storage (e.g., save like/dislike to database or analytics)
    raise NotImplementedError("The 'like' callback is not yet implemented.")


def app_block() -> Blocks:
    """Creates and returns the main Gradio Blocks interface for the Chattr app.

    This function sets up the user interface, including video, audio, chatbot, and input controls.

    Returns:
        Blocks: The constructed Gradio Blocks interface for the chat application.
    """
    with Blocks() as chat:
        with Row():
            with Column():
                video = PlayableVideo()
                audio = Audio(sources="upload", type="filepath")
            with Column():
                chatbot = Chatbot(
                    type="messages", show_copy_button=True, show_share_button=True
                )
                msg = Textbox()
                with Row():
                    button = Button("Send", variant="primary")
                    ClearButton([msg, chatbot, video], variant="stop")
        chatbot.like(like)
        button.click(graph.generate_response, [msg, chatbot], [msg, chatbot, audio])
        msg.submit(graph.generate_response, [msg, chatbot], [msg, chatbot, audio])
    return chat
