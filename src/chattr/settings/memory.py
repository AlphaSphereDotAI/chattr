from pydantic import BaseModel, Field


class MemorySettings(BaseModel):
    """Settings for memory configuration."""

    collection_name: str = Field(default="memories")
    embedding_dims: int = Field(default=384)
