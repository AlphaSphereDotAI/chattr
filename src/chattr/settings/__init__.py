"""Settings for the Chattr app."""
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

from chattr.settings.agent import AgentSettings
from chattr.settings.directory import DirectorySettings
from chattr.settings.embedder import EmbedderSettings
from chattr.settings.logger import LoggerSettings
from chattr.settings.mcp import (
    ExtraMCPServerSettings,
    VideoGeneratorMCPServerSettings,
    VoiceGeneratorMCPServerSettings,
)
from chattr.settings.memory import MemorySettings
from chattr.settings.model import ModelSettings
from chattr.settings.queue import QueueSettings
from chattr.settings.vector_database import VectorDatabaseSettings

__all__ = [
    "AgentSettings",
    "DirectorySettings",
    "EmbedderSettings",
    "ExtraMCPServerSettings",
    "LoggerSettings",
    "MemorySettings",
    "ModelSettings",
    "QueueSettings",
    "VectorDatabaseSettings",
    "VideoGeneratorMCPServerSettings",
    "VoiceGeneratorMCPServerSettings",
]

class Settings(BaseSettings):
    """Configuration for the Chattr app."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_parse_none_str="None",
        env_file=".env",
        extra="ignore",
    )

    directory: DirectorySettings = Field(default_factory=DirectorySettings, frozen=True)
    model: ModelSettings = Field(default_factory=ModelSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    vector_database: VectorDatabaseSettings = Field(
        default_factory=VectorDatabaseSettings
    )
    voice_generator_mcp_server: VoiceGeneratorMCPServerSettings = Field(
        default_factory=VoiceGeneratorMCPServerSettings
    )
    video_generator_mcp_server: VideoGeneratorMCPServerSettings = Field(
        default_factory=VideoGeneratorMCPServerSettings
    )
    extra_mcp_servers: list[ExtraMCPServerSettings] = Field(default_factory=list)
    log: LoggerSettings = Field(default_factory=LoggerSettings)
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: PositiveInt = Field(default=7777)
    queue: QueueSettings = Field(default_factory=QueueSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)


if __name__ == "__main__":
    from rich import print as rprint

    rprint(Settings().model_dump_json(indent=4))
