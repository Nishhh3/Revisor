from contextlib import asynccontextmanager

from fastapi import FastAPI

import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PRISM API...")

    yield

    logger.info("Stopping PRISM API...")