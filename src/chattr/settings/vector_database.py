from pydantic import BaseModel, Field, HttpUrl

from chattr.settings.embedder import EmbedderSettings


class VectorDatabaseSettings(BaseModel):
    """Settings for vector database configuration."""

    name: str = Field(default="chattr")
    url: HttpUrl = HttpUrl("http://localhost:6333")
    embedder: EmbedderSettings = Field(default_factory=EmbedderSettings)
