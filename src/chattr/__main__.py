from chainlit import (
    on_chat_start,
    on_message,
    Message,
    context,
    LangchainCallbackHandler,
)
from chainlit.cli import run_chainlit
from chattr import logger, GRAPH
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage


def main() -> None:
    @on_chat_start
    def on_start() -> None:
        logger.info("A new chat session has started!")

    @on_message
    async def on_messaging(msg: Message):
        config = {"configurable": {"thread_id": context.session.id}}
        cb = LangchainCallbackHandler()
        final_answer = Message(content="")

        for stream_msg, metadata in GRAPH.graph.stream(
            {"messages": [HumanMessage(content=msg.content)]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config),
        ):
            if (
                stream_msg.content
                and not isinstance(stream_msg, HumanMessage)
                and metadata["langgraph_node"] == "final"
            ):
                await final_answer.stream_token(stream_msg.content)

        await final_answer.send()

    run_chainlit(__file__)


if __name__ == "__main__":
    main()
