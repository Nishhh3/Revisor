"""
Repository ingestion for RAG -- fetches repo files, chunks them,
embeds them, and stores them in Qdrant.

Deliberately simple: fixed-size character chunking, not AST-aware.
Good enough for a first working version -- revisit with smarter
chunking once retrieval quality is actually measured, not before.
"""

import logging
import uuid

from fastembed import TextEmbedding
from github import Github
from qdrant_client import QdrantClient, models

from app.config import settings

logger = logging.getLogger("prism.rag.ingestion")

SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".lock", ".zip", ".pdf"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".next", "dist", "build", "venv", ".venv"}
MAX_FILE_SIZE = 50_000
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")
_embedding_model = None


def get_embedding_model() -> TextEmbedding:
    """Lazy-load once per process -- loading the model is slow, don't repeat it per call."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model (downloads on first run)")
        _embedding_model = TextEmbedding()  # defaults to BAAI/bge-small-en-v1.5, 384-dim
    return _embedding_model


def _should_skip(path: str, size: int) -> bool:
    if size > MAX_FILE_SIZE:
        return True
    if any(f"/{d}/" in f"/{path}/" for d in SKIP_DIRS):
        return True
    if any(path.endswith(ext) for ext in SKIP_EXTENSIONS):
        return True
    return False


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks


def _make_point_id(repo: str, file_path: str, chunk_index: int) -> str:
    """Deterministic ID -- re-running ingestion updates existing points
    instead of duplicating them, and different repos/files never collide."""
    return str(uuid.uuid5(_NAMESPACE, f"{repo}:{file_path}:{chunk_index}"))


def ingest_repository(repo_full_name: str) -> int:
    """Fetch, chunk, embed, and upsert every source file in a repo's
    default branch. Returns the number of chunks indexed."""
    gh = Github(settings.github_api_token)
    repo = gh.get_repo(repo_full_name)
    model = get_embedding_model()

    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )

    contents = repo.get_contents("")
    files_to_index = []
    while contents:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path))
        elif not _should_skip(item.path, item.size or 0):
            files_to_index.append(item)

    points = []
    for file_item in files_to_index:
        try:
            file_text = file_item.decoded_content.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            continue

        for i, chunk in enumerate(_chunk_text(file_text)):
            embedding = list(model.embed([chunk]))[0]
            points.append(models.PointStruct(
                id=_make_point_id(repo_full_name, file_item.path, i),
                vector=embedding.tolist(),
                payload={"repo": repo_full_name, "file_path": file_item.path, "text": chunk},
            ))

    if points:
        client.upsert(collection_name=settings.qdrant_collection, points=points)

    logger.info("Indexed %d chunks from %d files in %s", len(points), len(files_to_index), repo_full_name)
    return len(points)