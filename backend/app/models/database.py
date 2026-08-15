"""
PostgreSQL connection. Kept synchronous to match the rest of the
webhook path -- fetch_pr_context and review_logic_performance are
already blocking calls inside the async handler, so a sync DB layer
here doesn't introduce a new inconsistency. Async everywhere is a
step-6-with-Celery concern, not now.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()