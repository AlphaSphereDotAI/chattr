from gradio import (
    Blocks,
    Button,
    Chatbot,
    ChatMessage,
)


def generate_response(history):
    history.append(
        ChatMessage(
            role="assistant",
            content="The weather API says it is 20 degrees Celsius in New York.",
            metadata={
                "title": "🛠️ Used tool Weather API",
                "id": "",
                "parent_id": "",
                "duration": "",
                "status": "",
            },
        )
    )
    return history


def app_block() -> Blocks:
    """Create and return the main application interface.

    :return: Blocks: The complete Gradio application interface
    """

    history = [
        ChatMessage(role="assistant", content="How can I help you?"),
        ChatMessage(role="user", content="Can you make me a plot of quarterly sales?"),
        ChatMessage(
            role="assistant", content="I am happy to provide you that report and plot."
        ),
    ]
    with Blocks() as app:
        chatbot: Chatbot = Chatbot(history, type="messages")
        stream_btn: Button = Button(value="Generate", variant="primary")
        stream_btn.click(generate_response, chatbot, chatbot)
        # with Row():
        #     with Column():
        #         with Row():
        #         speed: Slider = Slider(
        #     with Column():
        #         out_audio: Audio = Audio(
        #         with Row():
    return app
