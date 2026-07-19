import logging

from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
import app.database.models

import app.auth.model

import app.repositories.model


setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Multi-Agent Pull Request Review Platform",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running"
    }


logger.info("PRISM API initialized successfully.")