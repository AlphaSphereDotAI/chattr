"""This module contains the settings for the Chattr app."""

from logging import getLogger
from pathlib import Path
from typing import List, Literal, Self

from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    HttpUrl,
    RedisDsn,
    SecretStr,
    StrictStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import head

logger = getLogger(__name__)


class ModelSettings(BaseModel):
    url: HttpUrl | None = Field(default=None)
    name: StrictStr | None = Field(default=None)
    api_key: SecretStr | None = Field(default=None)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_endpoint(self) -> Self:
        """
        Validate that the model endpoint URL is reachable.
        This method checks the HTTP status code of the provided URL and raises an error if it is not reachable.

        Returns:
            Self: The validated ModelSettings instance.

        Raises:
            ValueError: If the model's endpoint is unreachable.
        """
        if self.url and 200 > head(self.url, timeout=10).status_code >= 300:
            logger.error("Model's endpoint is unreachable")
            raise ValueError("Model's endpoint is unreachable")
        return self

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
                raise ValueError(
                    "You need to provide API Key for the Model provider via `MODEL__API_KEY`"
                )
            if not self.name:
                raise ValueError("You need to provide Model name via `MODEL__API_KEY`")
        return self


class ShortTermMemorySettings(BaseModel):
    url: RedisDsn = Field(default=RedisDsn(url="redis://localhost:6379"))


class VectorDatabaseSettings(BaseModel):
    name: StrictStr = Field(default="chattr")


class MCPSettings(BaseModel):
    name: StrictStr = Field(default=None)
    url: HttpUrl = Field(default=None)
    command: StrictStr = Field(default=None)
    args: List[StrictStr] = Field(default=[])
    transport: Literal["sse", "stdio"] = Field(default=None)


class DirectorySettings(BaseModel):
    base: DirectoryPath = Field(default_factory=lambda: Path.cwd())
    assets: DirectoryPath = Field(default_factory=lambda: Path.cwd() / "assets")
    log: DirectoryPath = Field(default_factory=lambda: Path.cwd() / "logs")
    image: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "image"
    )
    audio: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "audio"
    )
    video: DirectoryPath = Field(
        default_factory=lambda: Path.cwd() / "assets" / "video"
    )

    @model_validator(mode="after")
    def create_missing_dirs(self) -> Self:
        """
        Ensure that all specified directories exist, creating them if necessary.
        This method checks and creates any missing directories defined in the DirectorySettings.

        Args:
            values: A dictionary of directory paths to validate and create.

        Returns:
            dict: A dictionary of directory paths to validate and create.
        """
        directories = [
            self.base,
            self.assets,
            self.log,
            self.image,
            self.audio,
            self.video,
        ]
        logger.info(f"Creating directories: {directories}")
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
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
    short_term_memory: ShortTermMemorySettings = ShortTermMemorySettings()
    vector_database: VectorDatabaseSettings = VectorDatabaseSettings()
    voice_generator_mcp: MCPSettings = MCPSettings(
        url="http://localhost:8080/gradio_api/mcp/sse",
        transport="sse",
        name="voice_generator",
    )
    video_generator_mcp: MCPSettings = MCPSettings(
        url="http://localhost:8002/gradio_api/mcp/sse",
        transport="sse",
        name="video_generator",
    )
    directory: DirectorySettings = DirectorySettings()


if __name__ == "__main__":
    print(Settings().model_dump())
