from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import List, Literal, Self

from pydantic import (
    Field,
    FilePath,
    HttpUrl,
    SecretStr,
    StrictFloat,
    StrictStr,
    model_validator,
)
from pydantic_settings import BaseSettings
from requests import head

logger = getLogger(__name__)


class ModelSettings(BaseSettings):
    url: HttpUrl = Field(default="https://api.groq.com/openai/v1")
    name: StrictStr = Field(default="llama3-70b-8192")
    api_key: SecretStr = Field(default="not-needed")
    temperature: StrictFloat = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_local_path_conflict(self) -> Self:
        if 200 > head(self.url, timeout=10).status_code >= 300:
            logger.error("Model's endpoint is unreachable")
            raise ValueError("Model's endpoint is unreachable")
        return self


class ShortTermMemorySettings(BaseSettings):
    url: HttpUrl = Field(default="redis://localhost:6379")


class VectorDatabaseSettings(BaseSettings):
    name: StrictStr = Field(default="chattr")


class MCPSettings(BaseSettings):
    url: HttpUrl = Field(default="http://localhost:8001/gradio_api/mcp/sse")
    command: StrictStr = Field(default="uvx")
    args: List[StrictStr] = Field(default="chattr")
    transport: Literal["sse", "stdio"]


class Settings(BaseSettings):
    """Configuration for the Chattr app."""

    model = ModelSettings()
    short_term_memory = ShortTermMemorySettings()
    vector_database = VectorDatabaseSettings()
    voice_generator_mcp = MCPSettings(
        url="http://localhost:8001/gradio_api/mcp/sse", transport="sse"
    )
    video_generator_mcp = MCPSettings(
        url="http://localhost:8002/gradio_api/mcp/sse", transport="sse"
    )

    current_date: StrictStr = Field(
        default=datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")
    )

    base_dir: FilePath = Field(default=Path.cwd())
    assets_dir: FilePath = base_dir / "assets"
    log_dir: FilePath = base_dir / "logs"
    image_dir: FilePath = assets_dir / "image"
    audio_dir: FilePath = assets_dir / "audio"
    video_dir: FilePath = assets_dir / "video"
    log_file_path: FilePath = log_dir / f"{current_date}.log"
    audio_file_path: FilePath = audio_dir / f"{current_date}.wav"
    video_file_path: FilePath = video_dir / f"{current_date}.mp4"

    def model_post_init(self, __context):
        logger.info("Creating required directories...")
        try:
            self._create_required_dirs()
            logger.debug(f"All directories created successfully at {self.base_dir}")
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            raise

    def _create_required_dirs(self):
        self.assets_dir.mkdir(exist_ok=True)
        self.image_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        self.video_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
