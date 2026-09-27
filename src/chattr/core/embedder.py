from agno.knowledge.embedder.base import Embedder
from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
from agno.knowledge.embedder.google import GeminiEmbedder

from chattr.settings import EmbedderSettings


def setup_embedder(embedder: EmbedderSettings) -> Embedder:
    """Set up the embedder for the vector database."""
    match embedder.provider:
        case "google":
            return GeminiEmbedder(
                id=embedder.model_id,
                dimensions=embedder.dimensions,
                enable_batch=embedder.enable_batch,
                batch_size=embedder.batch_size,
            )
        case "fastembed":
            return FastEmbedEmbedder(
                id=embedder.model_id,
                dimensions=embedder.dimensions,
                enable_batch=embedder.enable_batch,
                batch_size=embedder.batch_size,
            )
        case _:
            _msg = f"Invalid provider: {embedder.provider}"
            raise ValueError(_msg)
