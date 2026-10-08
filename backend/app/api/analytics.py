"""Admin analytics endpoints.

Every endpoint counts only the LATEST review of each (repository, pr_number),
so reopened PRs and re-pushes don't inflate totals. Every endpoint accepts an
optional ?repository=owner/name filter.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# One review per PR (the newest), optionally limited to one repository.
LATEST = """
WITH latest AS (
  SELECT DISTINCT ON (repository, pr_number) *
  FROM reviews
  WHERE CAST(:repo AS text) IS NULL OR repository = CAST(:repo AS text)
  ORDER BY repository, pr_number, created_at DESC
)
"""


def _rows(db: Session, sql: str, params: Optional[dict] = None) -> list[dict]:
    params = {"repo": None, **(params or {})}
    return [dict(r._mapping) for r in db.execute(text(LATEST + sql), params)]


@router.get("/repositories")
def repositories(db: Session = Depends(get_db)):
    # Not filtered by repo: this feeds the filter dropdown itself.
    return _rows(
        db,
        """
        SELECT repository, COUNT(*) AS prs, COALESCE(SUM(finding_count), 0) AS findings
        FROM latest
        GROUP BY repository
        ORDER BY prs DESC
        """,
    )


@router.get("/summary")
def summary(repository: Optional[str] = None, db: Session = Depends(get_db)):
    row = _rows(
        db,
        """
        SELECT
          COUNT(*)                                           AS total_reviews,
          COALESCE(SUM(finding_count), 0)                    AS total_findings,
          COALESCE(ROUND(AVG(finding_count)::numeric, 2), 0) AS avg_findings_per_review,
          COUNT(*) FILTER (WHERE finding_count = 0)          AS clean_reviews,
          COUNT(DISTINCT repository)                         AS repositories,
          (SELECT COUNT(*) FROM findings f JOIN latest l2 ON l2.id = f.review_id
            WHERE f.severity = 'high')                       AS high_severity_findings
        FROM latest
        """,
        {"repo": repository},
    )[0]
    total = row["total_reviews"] or 0
    row["clean_rate"] = round(100 * row["clean_reviews"] / total, 1) if total else 0
    return row


@router.get("/severity")
def severity(repository: Optional[str] = None, db: Session = Depends(get_db)):
    return _rows(
        db,
        """
        SELECT f.severity, COUNT(*) AS count
        FROM findings f JOIN latest l ON l.id = f.review_id
        GROUP BY f.severity
        """,
        {"repo": repository},
    )


@router.get("/agents")
def agents(repository: Optional[str] = None, db: Session = Depends(get_db)):
    return _rows(
        db,
        """
        SELECT f.agent_type,
               COUNT(*) FILTER (WHERE f.severity = 'high')   AS high,
               COUNT(*) FILTER (WHERE f.severity = 'medium') AS medium,
               COUNT(*) FILTER (WHERE f.severity = 'low')    AS low,
               COUNT(*)                                      AS total
        FROM findings f JOIN latest l ON l.id = f.review_id
        GROUP BY f.agent_type
        ORDER BY total DESC
        """,
        {"repo": repository},
    )


@router.get("/timeline")
def timeline(
    repository: Optional[str] = None,
    days: int = Query(60, ge=1, le=365),
    db: Session = Depends(get_db),
):
    return _rows(
        db,
        """
        SELECT to_char(date_trunc('day', created_at), 'YYYY-MM-DD') AS day,
               COUNT(*)                        AS reviews,
               COALESCE(SUM(finding_count), 0) AS findings
        FROM latest
        WHERE created_at >= now() - make_interval(days => :days)
        GROUP BY 1
        ORDER BY 1
        """,
        {"repo": repository, "days": days},
    )


@router.get("/hotspots")
def hotspots(
    repository: Optional[str] = None,
    limit: int = Query(8, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return _rows(
        db,
        """
        SELECT f.file_path,
               COUNT(*) AS findings,
               COUNT(*) FILTER (WHERE f.severity = 'high') AS high,
               COUNT(DISTINCT f.review_id) AS reviews
        FROM findings f JOIN latest l ON l.id = f.review_id
        GROUP BY f.file_path
        ORDER BY findings DESC
        LIMIT :limit
        """,
        {"repo": repository, "limit": limit},
    )


@router.get("/recurring")
def recurring(repository: Optional[str] = None, db: Session = Depends(get_db)):
    """Keyword-bucketed issue types. Replace the CASE with GROUP BY category
    once agents emit a `category` field."""
    return _rows(
        db,
        """
        SELECT pattern, COUNT(*) AS count, COUNT(DISTINCT review_id) AS reviews
        FROM (
          SELECT f.review_id,
            CASE
              WHEN f.issue ILIKE '%mutable default%'                        THEN 'Mutable default argument'
              WHEN f.issue ILIKE '%assignment operator%'                    THEN 'Assignment instead of comparison'
              WHEN f.issue ILIKE '%parenthesis%' OR f.issue ILIKE '%syntax%' THEN 'Syntax error'
              WHEN f.issue ILIKE '%credential%' OR f.issue ILIKE '%password%' THEN 'Hardcoded credentials'
              WHEN f.issue ILIKE '%exception%'                              THEN 'Broad exception handling'
              WHEN f.issue ILIKE '%O(n%' OR f.issue ILIKE '%performance%'   THEN 'Inefficient lookup'
              WHEN f.issue ILIKE '%empty%' OR f.issue ILIKE '%zero%'        THEN 'Missing empty-input guard'
              WHEN f.issue ILIKE '%does not return%'                        THEN 'Missing return value'
              ELSE 'Other'
            END AS pattern
          FROM findings f JOIN latest l ON l.id = f.review_id
        ) t
        GROUP BY pattern
        ORDER BY count DESC
        """,
        {"repo": repository},
    )


@router.get("/developers")
def developers(repository: Optional[str] = None, db: Session = Depends(get_db)):
    """Per-developer view, keyed by the anonymised author hash."""
    return _rows(
        db,
        """
        SELECT l.pr_author_hash AS developer,
               COUNT(DISTINCT l.id)                          AS prs,
               COUNT(f.id)                                   AS findings,
               COUNT(f.id) FILTER (WHERE f.severity = 'high') AS high,
               ROUND(COUNT(f.id)::numeric / NULLIF(COUNT(DISTINCT l.id), 0), 2) AS findings_per_pr
        FROM latest l LEFT JOIN findings f ON f.review_id = l.id
        WHERE l.pr_author_hash IS NOT NULL
        GROUP BY l.pr_author_hash
        ORDER BY findings DESC
        """,
        {"repo": repository},
    )


@router.get("/recent")
def recent(
    repository: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return _rows(
        db,
        """
        SELECT l.id, l.repository, l.pr_number, l.pr_title, l.finding_count, l.created_at,
               (SELECT COUNT(*) FROM findings f
                 WHERE f.review_id = l.id AND f.severity = 'high') AS high_count
        FROM latest l
        ORDER BY l.created_at DESC
        LIMIT :limit
        """,
        {"repo": repository, "limit": limit},
    )