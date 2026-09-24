from agno.knowledge.embedder.fastembed import FastEmbedEmbedder

from chattr.settings import EmbedderSettings


def setup_embedder(embedder: EmbedderSettings) -> FastEmbedEmbedder:
    """Set up the embedder for the vector database."""
    return FastEmbedEmbedder(
        id=embedder.model_id,
        dimensions=embedder.dimensions,
        enable_batch=embedder.enable_batch,
        batch_size=embedder.batch_size,
    )
