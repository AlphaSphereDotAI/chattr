from pydantic import BaseModel, Field, PositiveInt


class EmbedderSettings(BaseModel):
    """Settings for embedder configuration."""

    model_id: str = Field(default="BAAI/bge-small-en-v1.5", description="The model ID to use for embedding.")
    dimensions: PositiveInt = Field(default=384, description="The dimensions of the embedding.")
    enable_batch: bool = Field(default=True, description="Whether to enable batching for embedding.")
    batch_size: PositiveInt = Field(default=100, description="The batch size for embedding.")
