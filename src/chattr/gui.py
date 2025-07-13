import gradio
from gradio import Blocks, Button, Chatbot, ChatMessage, Row, Textbox


def generate_response(history, thread_id):
    """
    Appends an assistant message about a quarterly sales plot to the chat history for the specified thread ID.

    If the thread ID is 0, raises a Gradio error prompting for a valid thread ID.

    Returns:
        The updated chat history including the new assistant message.
    """
    if thread_id == 0:
        gradio.Error("Please enter a thread ID.")
    history.append(
        ChatMessage(
            role="assistant",
            content=f"Here is the plot of quarterly sales for {thread_id}.",
            metadata={
                "title": "🛠️ Used tool Weather API",
            },
        )
    )
    return history


def app_block() -> Blocks:
    """
    Constructs and returns the main Gradio chat application interface with a thread ID input, chatbot display, and control buttons.

    Returns:
        Blocks: The complete Gradio Blocks interface for the chat application.
    """

    history = [
        ChatMessage(role="assistant", content="How can I help you?"),
        ChatMessage(role="user", content="Can you make me a plot of quarterly sales?"),
        ChatMessage(
            role="assistant",
            content="I am happy to provide you that report and plot.",
        ),
    ]
    with Blocks() as app:
        with Row():
            thread_id: Textbox = Textbox(label="Thread ID", info="Enter Thread ID")

        chatbot: Chatbot = Chatbot(history, type="messages")

        with Row():
            generate_btn: Button = Button(value="Generate", variant="primary")
            stop_btn: Button = Button(value="Stop", variant="stop")
        _event = generate_btn.click(generate_response, [chatbot, thread_id], chatbot)
        stop_btn.click(cancels=[_event])
    return app
