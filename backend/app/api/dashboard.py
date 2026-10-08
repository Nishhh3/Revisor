"""Admin analytics endpoints.

Assumptions (adjust to match your project):
  * models/database.py exposes a `get_db` FastAPI dependency yielding a SQLAlchemy Session
  * Supabase tables are named `reviews` and `findings`
Register in main.py:
    from app.api.dashboard import router as dashboard_router
    app.include_router(dashboard_router)
and make sure CORS allows your frontend origin.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.database import get_db  # adjust import if yours differs

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _rows(db: Session, sql: str, params: Optional[dict] = None) -> list[dict]:
    return [dict(r._mapping) for r in db.execute(text(sql), params or {})]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    row = _rows(
        db,
        """
        SELECT
          COUNT(*)                                            AS total_reviews,
          COALESCE(SUM(finding_count), 0)                     AS total_findings,
          COALESCE(ROUND(AVG(finding_count)::numeric, 2), 0)  AS avg_findings_per_review,
          COUNT(*) FILTER (WHERE finding_count = 0)           AS clean_reviews,
          COUNT(DISTINCT repository)                          AS repositories
        FROM reviews
        """,
    )[0]
    high = _rows(db, "SELECT COUNT(*) AS n FROM findings WHERE severity = 'high'")[0]["n"]
    total = row["total_reviews"] or 0
    row["clean_rate"] = round(100 * row["clean_reviews"] / total, 1) if total else 0
    row["high_severity_findings"] = high
    return row


@router.get("/severity")
def severity(repository: Optional[str] = None, db: Session = Depends(get_db)):
    return _rows(
        db,
        """
        SELECT f.severity, COUNT(*) AS count
        FROM findings f JOIN reviews r ON r.id = f.review_id
        WHERE (:repo IS NULL OR r.repository = :repo)
        GROUP BY f.severity
        """,
        {"repo": repository},
    )


@router.get("/agents")
def agents(db: Session = Depends(get_db)):
    """Findings per agent, split by severity."""
    return _rows(
        db,
        """
        SELECT agent_type,
               COUNT(*) FILTER (WHERE severity = 'high')   AS high,
               COUNT(*) FILTER (WHERE severity = 'medium') AS medium,
               COUNT(*) FILTER (WHERE severity = 'low')    AS low,
               COUNT(*)                                    AS total
        FROM findings
        GROUP BY agent_type
        ORDER BY total DESC
        """,
    )


@router.get("/timeline")
def timeline(days: int = Query(60, ge=1, le=365), db: Session = Depends(get_db)):
    return _rows(
        db,
        """
        SELECT to_char(date_trunc('day', created_at), 'YYYY-MM-DD') AS day,
               COUNT(*)                     AS reviews,
               COALESCE(SUM(finding_count), 0) AS findings
        FROM reviews
        WHERE created_at >= now() - make_interval(days => :days)
        GROUP BY 1
        ORDER BY 1
        """,
        {"days": days},
    )


@router.get("/hotspots")
def hotspots(limit: int = Query(8, ge=1, le=50), db: Session = Depends(get_db)):
    """Files that attract the most findings."""
    return _rows(
        db,
        """
        SELECT file_path,
               COUNT(*) AS findings,
               COUNT(*) FILTER (WHERE severity = 'high') AS high,
               COUNT(DISTINCT review_id) AS reviews
        FROM findings
        GROUP BY file_path
        ORDER BY findings DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )


@router.get("/recurring")
def recurring(db: Session = Depends(get_db)):
    """Recurring issue patterns.

    Stopgap: buckets findings by keywords in the issue text. Once agents emit a
    `category` field (recommended), replace the CASE with GROUP BY category.
    """
    return _rows(
        db,
        """
        SELECT pattern, COUNT(*) AS count, COUNT(DISTINCT review_id) AS reviews
        FROM (
          SELECT review_id,
            CASE
              WHEN issue ILIKE '%mutable default%'                       THEN 'Mutable default argument'
              WHEN issue ILIKE '%assignment operator%'                   THEN 'Assignment instead of comparison'
              WHEN issue ILIKE '%parenthesis%' OR issue ILIKE '%syntax%' THEN 'Syntax error'
              WHEN issue ILIKE '%credential%' OR issue ILIKE '%password%' THEN 'Hardcoded credentials'
              WHEN issue ILIKE '%exception%'                             THEN 'Broad exception handling'
              WHEN issue ILIKE '%O(n%' OR issue ILIKE '%performance%'    THEN 'Inefficient lookup'
              WHEN issue ILIKE '%empty%' OR issue ILIKE '%zero%'         THEN 'Missing empty-input guard'
              WHEN issue ILIKE '%does not return%'                       THEN 'Missing return value'
              ELSE 'Other'
            END AS pattern
          FROM findings
        ) t
        GROUP BY pattern
        ORDER BY count DESC
        """,
    )


@router.get("/recent")
def recent(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    return _rows(
        db,
        """
        SELECT r.id, r.repository, r.pr_number, r.pr_title, r.finding_count, r.created_at,
               COUNT(f.id) FILTER (WHERE f.severity = 'high') AS high_count
        FROM reviews r LEFT JOIN findings f ON f.review_id = r.id
        GROUP BY r.id
        ORDER BY r.created_at DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )