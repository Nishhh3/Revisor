import hashlib
import hmac
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.config import settings
from app.ingestion.pr_fetcher import fetch_pr_context
from app.agents.logic_performance_agent import review_logic_performance
from app.output.pr_commenter import post_findings_comment
from app.models.review_store import save_review
from app.agents.security_agent import SecurityAgent
from app.agents.standards_agent import StandardsAgent
from app.agents.base import AgentFinding
from app.agents.moderator import moderate

logger = logging.getLogger("prism.webhooks")
router = APIRouter()


def verify_signature(payload_body: bytes, signature_header: str | None) -> None:
    """
    GitHub signs each webhook payload with your GITHUB_WEBHOOK_SECRET.
    Reject anything that doesn't match -- this is your only defense
    against someone POSTing fake PR events at your endpoint.
    """
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")

    expected = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode(),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")



def run_review(repo_full_name: str, pr_number: int) -> None:
    """Run all review agents after the webhook response is sent."""
    try:
        pr_context = fetch_pr_context(repo_full_name, pr_number)

        logger.info(
            "Fetched PR context: title=%r files=%d diff_chars=%d",
            pr_context.title,
            len(pr_context.changed_files),
            len(pr_context.diff),
        )

        # 1. Logic and Performance Agent
        logic_findings = review_logic_performance(pr_context)

        if logic_findings is None:
            logger.error(
                "Logic/Performance agent failed; skipping review publication"
            )
            return

        # 2. Security Agent
        security_findings = []

        try:
            security_results = SecurityAgent().review(pr_context)

            security_findings = [
                {
                    "agent_type": "security",
                    "severity": finding.severity,
                    "file": finding.file,
                    "line": finding.line,
                    "issue": finding.message,
                    "recommendation": (
                        "Investigate the reported security issue "
                        "and apply an appropriate fix."
                    ),
                    "evidence": finding.evidence,
                }
                for finding in security_results
            ]
        except Exception:
            logger.exception(
                "Security Agent failed; continuing with other findings"
            )

        # 3. Standards Agent
        standards_findings = []

        try:
            standards_results = StandardsAgent().review(pr_context)

            standards_findings = [
                {
                    "agent_type": "standards",
                    "severity": finding.severity,
                    "file": finding.file,
                    "line": finding.line,
                    "issue": finding.message,
                    "recommendation": (
                        "Improve the code according to the identified "
                        "maintainability issue."
                    ),
                    "evidence": finding.evidence,
                }
                for finding in standards_results
            ]
        except Exception:
            logger.exception(
                "Standards Agent failed; continuing with other findings"
            )

        # Combine results for storage and GitHub comment
        raw_findings = logic_findings + security_findings + standards_findings

        agent_findings = [
            AgentFinding(
                agent_name=str(f.get("agent_type", f.get("category", "logic_performance"))),
                severity=str(f.get("severity", "low")).lower(),
                message=str(f.get("issue", "")),
                file=f.get("file"),
                line=f.get("line"),
                evidence=f.get("evidence", []) if isinstance(f.get("evidence", []), list) else [],
            )
            for f in raw_findings
        ]

        moderated_findings = moderate(agent_findings)

        findings = [
            {
                "agent_type": f.agent_name,
                "severity": f.severity,
                "file": f.file,
                "line": f.line,
                "issue": f.message,
                "recommendation": "Review the finding and apply an appropriate fix.",
                "evidence": f.evidence,
            }
            for f in moderated_findings
        ]

        for finding in findings:
            logger.info(
                "Finding: [%s] %s -- %s",
                finding.get("severity"),
                finding.get("file"),
                finding.get("issue"),
            )

        review_id = save_review(
            repo_full_name,
            pr_number,
            pr_context.title,
            pr_context.pr_author,
            findings,
        )
        logger.info("Saved review %s to database", review_id)

        post_findings_comment(repo_full_name, pr_number, findings)

    except Exception:
        logger.exception(
            "Review failed for %s PR #%s", repo_full_name, pr_number
        )



@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
):
    body = await request.body()
    verify_signature(body, x_hub_signature_256)

    payload = await request.json()
    action = payload.get("action")
    logger.info("Received GitHub event=%s action=%s", x_github_event, action)

    if x_github_event == "pull_request" and action in {"opened", "synchronize", "reopened"}:
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        logger.info("PR event queued: repo=%s pr=%s action=%s", repo_full_name, pr_number, action)
        background_tasks.add_task(run_review, repo_full_name, pr_number)

    return {"received": True}