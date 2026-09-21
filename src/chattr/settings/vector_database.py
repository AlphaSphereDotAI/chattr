from pydantic import BaseModel, Field, HttpUrl


class VectorDatabaseSettings(BaseModel):
    """Settings for vector database configuration."""

    name: str = Field(default="chattr")
    url: HttpUrl = HttpUrl("http://localhost:6333")
