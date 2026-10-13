"""
Usage: python -m app.scripts.ingest_repo <owner/repo>
"""
import sys

from app.rag.ingestion import ingest_repository

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.scripts.ingest_repo <owner/repo>")
        sys.exit(1)
    count = ingest_repository(sys.argv[1])
    print(f"Indexed {count} chunks from {sys.argv[1]}")