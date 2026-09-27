from typing import Literal

from pydantic import BaseModel, Field, PositiveInt


class EmbedderSettings(BaseModel):
    """Settings for embedder configuration."""

    provider: Literal["google", "fastembed"] = Field(
        default="google",
        description="The provider to use for embedding.",
    )
    model_id: str = Field(
        default="gemini-embedding-001",
        description="The model ID to use for embedding.",
    )
    dimensions: PositiveInt = Field(default=384, description="The dimensions of the embedding.")
    enable_batch: bool = Field(default=True, description="Whether to enable batching for embedding.")
    batch_size: PositiveInt = Field(default=100, description="The batch size for embedding.")
