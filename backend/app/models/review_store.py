# """
# Deliberately does NOT accept or store: diff text, source code, file
# contents, or raw PR author username. Only review metadata + findings.
# """
# import hashlib

# from app.models.database import SessionLocal
# from app.models.review import Review, Finding


# def hash_author(username: str | None) -> str | None:
#     if not username:
#         return None
#     return hashlib.sha256(username.encode()).hexdigest()[:16]


# def save_review(repo_full_name: str, pr_number: int, pr_title: str,
#                  pr_author: str | None, findings: list[dict],
#                  agent_type: str = "logic_performance") -> str:
#     db = SessionLocal()
#     try:
#         review = Review(
#             repository=repo_full_name,
#             pr_number=pr_number,
#             pr_title=pr_title,
#             pr_author_hash=hash_author(pr_author),
#             finding_count=len(findings),
#         )
#         db.add(review)
#         db.flush()  # populates review.id before we attach findings

#         for f in findings:
#             db.add(Finding(
#                 review_id=review.id,
#                 agent_type=agent_type,
#                 severity=f.get("severity", "low"),
#                 file_path=f.get("file"),
#                 issue=f.get("issue", ""),
#                 recommendation=f.get("recommendation"),
#             ))

#         db.commit()
#         return str(review.id)
#     finally:
#         db.close()


import hashlib

from app.models.database import SessionLocal
from app.models.review import Review, Finding, AgentRun


def hash_author(username: str | None) -> str | None:
    if not username:
        return None
    return hashlib.sha256(username.encode()).hexdigest()[:16]


def save_review(repo_full_name: str, pr_number: int, pr_title: str,
                 pr_author: str | None, findings: list[dict],
                 agent_type: str = "logic_performance",
                 agent_runs: list[dict] | None = None) -> str:
    db = SessionLocal()
    try:
        review = Review(
            repository=repo_full_name,
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author_hash=hash_author(pr_author),
            finding_count=len(findings),
        )
        db.add(review)
        db.flush()  # populates review.id before we attach findings

        for f in findings:
            evidence = f.get("evidence")
            db.add(Finding(
                review_id=review.id,
                agent_type=f.get("agent_type", agent_type),
                severity=f.get("severity", "low"),
                file_path=f.get("file"),
                line=f.get("line"),
                evidence=evidence if isinstance(evidence, list) else None,
                issue=f.get("issue", ""),
                recommendation=f.get("recommendation"),
            ))

        for r in agent_runs or []:
            db.add(AgentRun(
                review_id=review.id,
                agent_name=r["agent_name"],
                status=r["status"],
                duration_ms=r.get("duration_ms"),
                findings_raw=r.get("findings_raw", 0),
                findings_kept=r.get("findings_kept", 0),
            ))

        db.commit()
        return str(review.id)
    finally:
        db.close()