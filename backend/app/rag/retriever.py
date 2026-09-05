"""
Given a query, return the most relevant already-indexed chunks
for a specific repo -- scoped by repo so PRISM never leaks one
repo's code into another repo's review.
"""

import logging

from qdrant_client import QdrantClient, models

from app.config import settings
from app.rag.ingestion import get_embedding_model

logger = logging.getLogger("prism.rag.retriever")


def retrieve_context(repo_full_name: str, query: str, top_k: int = 3) -> list[dict]:
    model = get_embedding_model()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    query_vector = list(model.embed([query]))[0]

    results = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector.tolist(),
        query_filter=models.Filter(
            must=[models.FieldCondition(key="repo", match=models.MatchValue(value=repo_full_name))]
        ),
        limit=top_k,
    ).points

    return [
        {"file_path": r.payload["file_path"], "text": r.payload["text"], "score": r.score}
        for r in results
    ]