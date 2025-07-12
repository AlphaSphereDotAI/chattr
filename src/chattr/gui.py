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
        #         text: Textbox = Textbox(label="Input Text", info="Enter your text here")
        #         char_limit: Number = Number(label="Character Limit", value=-1)
        #         with Row():
        #             save_file: Checkbox = Checkbox(label="Save Audio File")
        #         speed: Slider = Slider(
        #             minimum=0.5,
        #             maximum=2,
        #             value=1,
        #             step=0.1,
        #             label="Speed"
        #         )
        #     with Column():
        #         out_audio: Audio = Audio(
        #             label="Output Audio",
        #             interactive=False,
        #             streaming=True,
        #             autoplay=True
        #         )
        #         with Row():
        #             stream_btn: Button = Button(value="Generate", variant="primary")
        #             stop_btn: Button = Button(value="Stop", variant="stop")
        # stream_event = stream_btn.click(
        #     fn=generate_audio_for_text,
        #     inputs=[text, voice, speed, save_file, debug, char_limit],
        #     outputs=[out_audio],
        # )
        # stop_btn.click(fn=None, cancels=stream_event)
    return app
