"""Main orchestration graph for the Chattr application."""

from json import loads

from agno.agent import Agent
from agno.db import BaseDb
from agno.db.json import JsonDb
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.knowledge.knowledge import Knowledge
from agno.models.openai.like import OpenAILike
from agno.tools import Toolkit
from agno.tools.mcp import MultiMCPTools
from agno.vectordb.qdrant import Qdrant
from gradio import Error
from poml import poml

from chattr.app.logger import logger
from chattr.app.settings import Settings
from chattr.app.utils import is_url


class ChattrAgent:
    """Chattr Agent."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def setup_agent(self) -> Agent:
        """Initialize the Chattr agent."""
        try:
            return Agent(
                model=self._setup_model(),
                tools=await self._setup_tools(),
                description="".join(
                    [
                        "You are a helpful assistant ",
                        f"who can act and mimic {self.settings.character.name}'s character ",
                        "and answer questions about the era.",
                    ]
                ),
                instructions=[
                    "Understand the user's question and context.",
                    "Gather relevant information and resources.",
                    f"Formulate a clear and concise response in {self.settings.character.name}'s voice.",
                    "ALWAYS generate audio from the formulated response using the appropriate Tool.",
                    "Generate video from the resulted audio using the appropriate Tool.",
                ],
                db=self._setup_database(),
                knowledge=self._setup_knowledge(
                    self._setup_vector_database(),
                    self._setup_database(),
                ),
                markdown=True,
                add_datetime_to_context=True,
                timezone_identifier=self.settings.timezone,
                pre_hooks=[PIIDetectionGuardrail(), PromptInjectionGuardrail()],
                debug_mode=True,
                save_response_to_file="agno/response.txt",
                add_history_to_context=True,
                add_memories_to_context=True,
            )
        except ValueError as e:
            _msg: str = f"Failed to initialize Agent: {e}"
            logger.error(_msg)
            raise Error(_msg, print_exception=self.settings.debug) from e

    async def _setup_tools(self) -> list[Toolkit]:
        if not self.settings.mcp.path.exists():
            return []
        mcp_servers: list[dict] = loads(self.settings.mcp.path.read_text()).get(
            "mcp_servers",
            [],
        )
        url_servers: list[dict] = [m for m in mcp_servers if m.get("type") == "url"]
        if not url_servers:
            return []
        self.mcp_tools = MultiMCPTools(
            urls=[m["url"] for m in url_servers],
            urls_transports=[m["transport"] for m in url_servers],
        )
        await self.mcp_tools.connect()
        return [self.mcp_tools]

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
        """
        if not self.settings.model.url:
            _msg = "Model URL is missing. Set it with `MODEL__URL`"
            logger.error(_msg)
            raise ValueError(_msg)
        if not is_url(str(self.settings.model.url)):
            _msg = "Model URL is invalid. Set it with `MODEL__URL`"
            logger.error(_msg)
            raise ValueError(_msg)
        if not self.settings.model.name:
            _msg = "Model name is missing. Set it with `MODEL__NAME`"
            logger.error(_msg)
            raise ValueError(_msg)
        if not self.settings.model.api_key:
            _msg = "API key is missing. Set it with `MODEL__API_KEY`"
            logger.error(_msg)
            raise ValueError(_msg)
        return OpenAILike(
            base_url=str(self.settings.model.url),
            id=self.settings.model.name,
            api_key=self.settings.model.api_key.get_secret_value(),
            temperature=self.settings.model.temperature,
            cache_response=True,
        )

    def _setup_vector_database(self) -> Qdrant:
        return Qdrant(
            collection=self.settings.vector_database.name,
            url=self.settings.vector_database.url.host,
        )

    def _setup_knowledge(self, vector_db: Qdrant, db: BaseDb) -> Knowledge:
        return Knowledge(
            vector_db=vector_db,
            contents_db=db,
        )

    def _setup_database(self) -> JsonDb:
        return JsonDb(
            db_path="agno",
        )

    async def _close(self) -> None:
        try:
            logger.info("Closing MCP tools...")
            await self.mcp_tools.close()
        except Exception as e:
            msg: str = f"Error closing MCP tools: {e}, Check if the Tool services are running."
            logger.error(msg)
            raise Error(msg, print_exception=self.settings.debug) from e
