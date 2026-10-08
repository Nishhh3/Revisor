"""
Dashboard API -- read-only endpoints serving review/finding data to
the frontend. No writes here; all writes happen via the webhook path
(review_store.save_review). Keeping this strictly read-only means the
dashboard can never accidentally corrupt review data.
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.database import SessionLocal
from app.models.review import Review
from sqlalchemy.orm import joinedload

router = APIRouter()


class FindingOut(BaseModel):
    id: UUID
    agent_type: str
    severity: str
    file_path: str | None
    issue: str
    recommendation: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewSummaryOut(BaseModel):
    id: UUID
    repository: str
    pr_number: int
    pr_title: str | None
    finding_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewDetailOut(ReviewSummaryOut):
    findings: list[FindingOut]


@router.get("/reviews", response_model=list[ReviewSummaryOut])
def list_reviews(limit: int = 50):
    """Most recent first, capped so the dashboard can't accidentally pull the whole table."""
    db = SessionLocal()
    try:
        return (
            db.query(Review)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


@router.get("/reviews/{review_id}", response_model=ReviewDetailOut)
def get_review(review_id: UUID):
    db = SessionLocal()
    try:
        review = (
            db.query(Review)
            .options(joinedload(Review.findings))
            .filter(Review.id == review_id)
            .first()
        )
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    finally:
        db.close()