"""Settings for the Chattr app."""

from pydantic import Field, IPvAnyAddress, PositiveInt
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, SettingsConfigDict

from chattr.settings.character import CharacterSettings
from chattr.settings.directory import DirectorySettings
from chattr.settings.logger import LoggerSettings
from chattr.settings.mcp import MCPSettings
from chattr.settings.memory import MemorySettings
from chattr.settings.model import ModelSettings
from chattr.settings.vector_database import VectorDatabaseSettings


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
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    character: CharacterSettings = Field(default_factory=CharacterSettings)
    log: LoggerSettings = Field(default_factory=LoggerSettings)
    debug: bool = Field(default=False)
    timezone: TimeZoneName = Field(default="Africa/Cairo")
    host: IPvAnyAddress = Field(default="0.0.0.0")
    port: PositiveInt = Field(default=7777)


if __name__ == "__main__":
    from rich import print as rprint

    rprint(Settings().model_dump_json(indent=4))
