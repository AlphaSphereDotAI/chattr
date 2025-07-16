from gradio import (
    Blocks,
    ChatMessage,
    Error,
    LikeData,
    TabbedInterface,
    ChatInterface,
    Request,
)


def generate_response(text, thread_id: str):
    """
    Appends an assistant message about a quarterly sales plot to the chat history for the specified thread ID.

    If the thread ID is 0, it raises a Gradio error prompting for a valid thread ID.

    Returns:
        The updated chat history including the new assistant message.
    """
    if thread_id == "0":
        raise Error("Please enter a thread ID.")

    yield [
        ChatMessage(
            role="assistant",
            content=f"{text} {thread_id}.",
            metadata={"title": "🛠️ Used tool Weather API"},
        )
    ]


def like(evt: LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)


def random_response(message, history, request: Request):
    print(request.session_hash)
    return f"{message} {history}"


def app_block() -> Blocks:
    """
    Constructs and returns the main Gradio chat application interface with a thread ID input, chatbot display, and control buttons.

    Returns:
        Blocks: The complete Gradio Blocks interface for the chat application.
    """

    chat = ChatInterface(random_response, type="messages", save_history=True)
    return TabbedInterface([chat], ["Chattr"])
