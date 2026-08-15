import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.webhooks import router as webhooks_router
from app.api.dashboard import router as dashboard_router
from app.config import settings

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger("prism")

app = FastAPI(
    title="PRISM",
    description="Multi-Agent AI System for Intelligent Pull Request Review",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])


@app.get("/health")
def health_check():
    """
    Build-step 1 target: this should return 200 once `docker-compose up`
    is running cleanly, before any agent or webhook code is trusted.
    """
    return {"status": "ok", "service": "prism-api", "env": settings.app_env}