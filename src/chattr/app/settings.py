"""Settings for the Chattr app."""

from json import dumps
from logging import FileHandler
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    FilePath,
    HttpUrl,
    SecretStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from chattr.app.logger import logger

load_dotenv()


class MemorySettings(BaseModel):
    """Settings for memory configuration."""

    collection_name: str = Field(default="memories")
    embedding_dims: int = Field(default=384)


class VectorDatabaseSettings(BaseModel):
    """Settings for vector database configuration."""

    name: str = Field(default="chattr")
    url: HttpUrl = HttpUrl("http://localhost:6333")


class MCPSettings(BaseModel):
    """Settings for MCP configuration."""

    path: FilePath = Path.cwd() / "mcp.json"

    @model_validator(mode="after")
    def create_init_mcp(self) -> Self:
        """Create an initial MCP config file if it does not exist."""
        if not self.path.exists():
            self.path.write_text(
                dumps(
                    {
                        "mcpServers": {
                            "time": {
                                "command": "docker",
                                "args": ["run", "-i", "--rm", "mcp/time"],
                            },
                            "sequential_thinking": {
                                "command": "docker",
                                "args": ["run", "-i", "--rm", "mcp/sequentialthinking"],
                            },
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            logger.info("`mcp.json` not found. Created initial MCP config file.")
        return self

    @model_validator(mode="after")
    def is_valid(self) -> Self:
        """Validate that the MCP config file is a JSON file."""
        if self.path and self.path.suffix != ".json":
            msg = "MCP config file must be a JSON file"
            raise ValueError(msg)
        return self


class DirectorySettings(BaseModel):
    """Settings for application directories."""

    base: DirectoryPath = Field(default_factory=Path.cwd, frozen=True)

    @computed_field
    @property
    def log(self) -> DirectoryPath:
        """Path to the log directory."""
        return self.base / "logs" / APP_NAME

    @computed_field
    @property
    def assets(self) -> DirectoryPath:
        """Path to the assets directory."""
        return self.base / "assets"

    @computed_field
    @property
    def audio(self) -> DirectoryPath:
        """Path to the audio directory."""
        return self.assets / "audio"

    @computed_field
    @property
    def video(self) -> DirectoryPath:
        """Path to the video directory."""
        return self.assets / "video"

    @computed_field
    @property
    def prompts(self) -> DirectoryPath:
        """Path to the prompts directory."""
        return self.assets / "prompts"

    @model_validator(mode="after")
    def create_missing_dirs(self) -> Self:
        """
        Ensure that all specified directories exist, creating them if necessary.

        Checks and creates any missing directories defined in the `DirectorySettings`.

        Returns:
            Self: The validated DirectorySettings instance.
        """
        for directory in [
            self.base,
            self.assets,
            self.log,
            self.audio,
            self.video,
            self.prompts,
        ]:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    logger.info("Created directory %s.", directory)
                    if directory == self.log:
                        logger.addHandler(FileHandler(self.log / "chattr.log"))
                except OSError as e:
                    logger.error("Error creating directory %s: %s", directory, e)
                    raise
        return self


class ModelSettings(BaseModel):
    """Settings related to model execution."""

    url: HttpUrl | None = Field(default=None)
    name: str | None = Field(default=None)
    api_key: SecretStr | None = Field(default=None)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_api_key_exist(self) -> Self:
        """
        Ensure that an API key and model name are provided if a model URL is set.

        This method validates the presence of required credentials for the model provider.

        Returns:
            Self: The validated ModelSettings instance.

        Raises:
            ValueError: If the API key or model name is missing when a model URL is provided.
        """
        if self.url:
            if not self.api_key or not self.api_key.get_secret_value():
                _msg = "You need to provide API Key for the Model provider via `MODEL__API_KEY`"
                raise ValueError(_msg)
            if not self.name:
                _msg = "You need to provide Model name via `MODEL__NAME`"
                raise ValueError(_msg)
        return self


class Settings(BaseSettings):
    """Configuration for the Chattr app."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_parse_none_str="None",
        env_file=".env",
        extra="ignore",
    )

    model: ModelSettings = ModelSettings()
    memory: MemorySettings = MemorySettings()
    vector_database: VectorDatabaseSettings = VectorDatabaseSettings()
    mcp: MCPSettings = MCPSettings()
    directory: DirectorySettings = DirectorySettings()
    debug: bool = False


if __name__ == "__main__":
    print(Settings().model_dump())
