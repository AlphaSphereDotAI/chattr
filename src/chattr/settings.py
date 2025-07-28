from logging import getLogger
from pathlib import Path
from typing import List, Literal, Self

from pydantic import (
    AnyUrl,
    BaseModel,
    DirectoryPath,
    Field,
    HttpUrl,
    RedisDsn,
    SecretStr,
    StrictStr,
    model_validator
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
        if self.url and 200 > head(self.url, timeout=10).status_code >= 300:
            logger.error("Model's endpoint is unreachable")
            raise ValueError("Model's endpoint is unreachable")
        return self

    @model_validator(mode="after")
    def check_api_key_exist(self) -> Self:
        if self.url and (self.api_key is None or not self.api_key.get_secret_value()):
            raise ValueError("You need to provide `MODEL__API_KEY`")
        return self


class ShortTermMemorySettings(BaseModel):
    url: AnyUrl = Field(default=RedisDsn(url="redis://localhost:6379"))


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

    @model_validator(mode="before")
    def create_missing_dirs(cls, values: dict) -> dict:
        directories: list[Path] = list(values.values())
        for directory in directories:
            directory.mkdir(exist_ok=True)
        return values


class Settings(BaseSettings):
    """Configuration for the Chattr app."""

    model_config = SettingsConfigDict(env_nested_delimiter="__", env_parse_none_str="None",env_file=".env", extra='ignore')

    model: ModelSettings = ModelSettings(    )
    short_term_memory: ShortTermMemorySettings = ShortTermMemorySettings()
    vector_database: VectorDatabaseSettings = VectorDatabaseSettings()
    voice_generator_mcp: MCPSettings = MCPSettings(
        url="http://localhost:8001/gradio_api/mcp/sse",
        transport="sse",
        name="voice_generator",
    )
    video_generator_mcp: MCPSettings = MCPSettings(
        url="http://localhost:8002/gradio_api/mcp/sse",
        transport="sse",
        name="video_generator",
    )
    directory: DirectorySettings = DirectorySettings()
    # log_file_path: FilePath = Field(default_factory=lambda: Path.cwd()  / "logs" / f"{datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")}.log")
    # audio_file_path: FilePath = Field(default_factory=lambda: Path.cwd()/ "assets" / "audio" / f"{datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")}.wav")
    # video_file_path: FilePath = Field(default_factory=lambda: Path.cwd() / "assets" / "video" / f"{datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")}.mp4")


if __name__ == "__main__":
    print(Settings().model_dump())
