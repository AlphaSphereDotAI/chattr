from typing import Any, List

from pydantic import StrictStr
from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean_non_ascii_chars  # type: ignore
from unstructured.cleaners.core import (
    bytes_string_to_string,
    clean_extra_whitespace,
    replace_unicode_quotes,
)
from unstructured.documents.elements import Element
from unstructured.partition.auto import partition

client = QdrantClient(host="localhost", port=6333)


def get_chunks(url: StrictStr) -> List[Element]:
    elements: List[Element] = partition(url=url)
    for i in range(len(elements)):
        elements[i].text = clean_non_ascii_chars(text=elements[i].text)
        elements[i].text = replace_unicode_quotes(text=elements[i].text)
        elements[i].text = clean_extra_whitespace(text=elements[i].text)
        elements[i].text = bytes_string_to_string(text=elements[i].text)
    return chunk_by_title(elements=elements)


def add_data(chunks: List[Element]) -> None:
    docs: List[StrictStr] = [chunks[i].text for i in range(len(chunks))]
    metadata: List[dict[str, Any]] = [
        chunks[i].metadata.to_dict() for i in range(len(chunks))
    ]
    ids = list(range(1, len(chunks) + 1))
    client.add(
        collection_name=settings.vector_database_name,
        documents=docs,
        metadata=metadata,
        ids=ids,
    )


def query_db(query: StrictStr) -> List[QueryResponse]:
    return client.query(
        collection_name=settings.vector_database_name,
        query_text=query,
    )


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Napoleon"
    chunks: List[Element] = get_chunks(url=url)
    add_data(chunks=chunks)
    r: List[QueryResponse] = query_db(query="Napoleon Bonaparte")
    print(len(r))
    print(r)
