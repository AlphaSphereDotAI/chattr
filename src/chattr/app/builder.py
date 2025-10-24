"""Main orchestration graph for the Chattr application."""

from collections.abc import AsyncGenerator
from json import dumps
from pathlib import Path

from agno.agent import Agent
from agno.db.json import JsonDb
from agno.knowledge.knowledge import Knowledge
from agno.models.message import Message
from agno.models.openai.like import OpenAILike
from agno.vectordb.qdrant import Qdrant
from gradio import (
    Audio,
    Blocks,
    Button,
    Chatbot,
    ChatMessage,
    ClearButton,
    Column,
    Error,
    Image,
    Markdown,
    Row,
    Sidebar,
    Textbox,
    Video,
)
from gradio.components.chatbot import MetadataDict
from m3u8 import M3U8, load
from poml import poml
from pydantic import FilePath, HttpUrl, ValidationError
from requests import Session

from chattr.app.settings import Settings, logger
from chattr.app.state import State


class App:
    """Main application class for the Chattr Multi-agent system app."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.agent = self._setup_agent()

    def _setup_agent(self) -> Agent:
        return Agent(
            model=self._setup_model(),
            # tools=self._setup_tools(),
            instructions=self._setup_prompt(),
            db=self._setup_database(),
            knowledge=self._setup_knowledge(self._setup_vector_database()),
            markdown=True,
        )

    def _setup_prompt(self) -> str:
        prompt_template = poml(
            self.settings.directory.prompts / "template.poml",
            {"character": "Napoleon"},
            chat=False,
            format="dict",
        )
        if not isinstance(prompt_template, dict):
            _msg = "Prompt template must be a string."
            raise TypeError(_msg)
        return prompt_template["messages"]

    def _setup_model(self) -> OpenAILike:
        """
        Initialize the ChatOpenAI language model using the provided settings.

        This method creates and returns a ChatOpenAI instance configured with
        the model's URL, name, API key, and temperature.

        Returns:
            ChatOpenAI: The initialized ChatOpenAI language model instance.

        Raises:
            Exception: If the model initialization fails.
        """
        try:
            return OpenAILike(
                base_url=str(self.settings.model.url),
                id=self.settings.model.name,
                api_key=self.settings.model.api_key,
                temperature=self.settings.model.temperature,
            )
        except Exception as e:
            _msg = f"Failed to initialize ChatOpenAI model: {e}"
            logger.error(_msg)
            raise Error(_msg) from e

    def _setup_vector_database(self) -> Qdrant:
        return Qdrant(
            collection=self.settings.vector_database.name,
            url=self.settings.vector_database.url.host,
        )

    def _setup_knowledge(self, vector_db: Qdrant) -> Knowledge:
        return Knowledge(
            vector_db=vector_db,
        )

    def _setup_database(self) -> JsonDb:
        return JsonDb(
            db_path="agno",
        )

    def gui(self) -> Blocks:
        """
        Creates and returns the main Gradio Blocks interface for the Chattr app.

        Returns:
            Blocks: The constructed Gradio Blocks interface for the chat application.
        """
        with Blocks() as chat:
            with Sidebar(visible=self.settings.debug):
                with Row():
                    with Column():
                        Markdown("# Model Prompt")
                        Markdown(self._setup_prompt())
            with Row():
                with Column():
                    video = Video(
                        label="Output Video",
                        interactive=False,
                        autoplay=True,
                        sources="upload",
                        format="mp4",
                    )
                    audio = Audio(
                        label="Output Audio",
                        interactive=False,
                        autoplay=True,
                        sources="upload",
                        type="filepath",
                        format="wav",
                    )
                with Column():
                    chatbot = Chatbot(
                        type="messages",
                        show_copy_button=True,
                        show_share_button=True,
                    )
                    msg = Textbox()
                    with Row():
                        button = Button("Send", variant="primary")
                        _ = ClearButton([msg, chatbot, video], variant="stop")
            _ = button.click(
                self.generate_response,
                [msg, chatbot],
                [msg, chatbot, audio, video],
            )
            _ = msg.submit(
                self.generate_response,
                [msg, chatbot],
                [msg, chatbot, audio, video],
            )
        return chat

    async def generate_response(
        self,
        message: str,
        history: list[ChatMessage],
    ) -> AsyncGenerator[tuple[str, list[ChatMessage], Path | None, Path | None]]:
        """
        Generate a response to a user message and update the conversation history.

        This asynchronous method streams responses from the state graph and
        yields updated history and audio file paths as needed.

        Args:
            message: The user's input message as a string.
            history: The conversation history as a list of ChatMessage objects.

        Returns:
            AsyncGenerator: Yields a tuple containing an
                            empty string, the updated history, and
                            a Path to an audio file if generated.
        """
        is_audio_generated: bool = False
        audio_file: FilePath | None = None
        last_agent_message: Message | None = None
        async for response in self.agent.arun(
            Message(content=message, role="user"),
            stream=True,
        ):
            logger.debug(f"Response type received: {response.keys()}")
            if response.keys() == {"agent"}:
                logger.debug(f"-------- Agent response {response}")
                last_agent_message: Message = response["agent"]["messages"][-1]
                if last_agent_message.tool_calls:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=dumps(
                                last_agent_message.tool_calls[0]["args"],
                                indent=4,
                            ),
                            metadata=MetadataDict(
                                title=last_agent_message.tool_calls[0]["name"],
                                id=last_agent_message.tool_calls[0]["id"],
                            ),
                        ),
                    )
                else:
                    history.append(
                        ChatMessage(
                            role="assistant",
                            content=last_agent_message.content,
                        ),
                    )
            elif response.keys() == {"tools"}:
                logger.debug(f"-------- Tool Message: {response}")
                last_tool_message: Message = response["tools"]["messages"][-1]
                history.append(
                    ChatMessage(
                        role="assistant",
                        content=last_tool_message.content,
                        metadata=MetadataDict(
                            title=last_tool_message.name,
                            id=last_tool_message.id,
                        ),
                    ),
                )
                if self._is_url(last_tool_message.content):
                    logger.info(f"Downloading audio from {last_tool_message.content}")
                    file_path: Path = (
                        self.settings.directory.audio / last_tool_message.id
                    )
                    audio_file = file_path.with_suffix(".wav")
                    self._download_file(last_tool_message.content, audio_file)
                    logger.info(f"Audio downloaded to {audio_file}")
                    is_audio_generated = True
                    yield "", history, audio_file, None
            else:
                _msg = f"Unsupported audio source: {response.keys()}"
                logger.warning(_msg)
                raise Error(_msg)
            yield "", history, audio_file if is_audio_generated else None, None

    def _is_url(self, value: str | None) -> bool:
        """
        Check if a string is a valid URL.

        Args:
            value: The string to check. Can be None.

        Returns:
            bool: True if the string is a valid URL, False otherwise.
        """
        if value is None:
            return False

        try:
            _ = HttpUrl(value)
            return True
        except ValidationError:
            return False

    def _download_file(self, url: HttpUrl, path: Path) -> None:
        """
        Download a file from a URL and save it to a local path.

        Args:
            url: The URL to download the file from.
            path: The local file path where the downloaded file will be saved.

        Returns:
            None

        Raises:
            requests.RequestException: If the HTTP request fails.
            IOError: If file writing fails.
        """
        if str(url).endswith(".m3u8"):
            _playlist: M3U8 = load(url)
            url: str = str(url).replace("playlist.m3u8", _playlist.segments[0].uri)
        logger.info(f"Downloading {url} to {path}")
        session = Session()
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"File downloaded to {path}")
