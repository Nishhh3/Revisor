# backend/reingest.py
import logging
logging.basicConfig(level=logging.INFO)

from app.rag.ingestion import ingest_repository

count = ingest_repository("Nikkk31/check")
print(f"Indexed {count} chunks")