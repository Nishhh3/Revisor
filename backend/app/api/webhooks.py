import hashlib
import hmac
import logging
import time

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
from app.agents.persona_agent import PersonaAgent

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


def generate_recommendation(finding: AgentFinding) -> str:
    """Generate a targeted remediation suggestion from a finding."""
    text = finding.message.lower()

    if any(term in text for term in (
        "hardcoded api key", "hardcoded credential",
        "hardcoded secret", "hard coded secret",
        "secret credential", "exposes a secret",
    )):
        return (
            "Remove the hardcoded credential, load it from an environment "
            "variable or secret manager, and rotate it if it was exposed."
        )

    if "md5" in text or "sha1" in text or "weak hash" in text:
        return (
            "Avoid MD5 or SHA-1 for security-sensitive hashing. Choose a "
            "modern algorithm appropriate to the use case; use a dedicated "
            "password-hashing algorithm for passwords."
        )

    if any(term in text for term in (
        "password", "verify_user", "credential validation",
    )) and any(term in text for term in (
        "truthy", "does not actually verify", "ignores the user_id",
        "authentication",
    )):
        return (
            "Verify the supplied credentials against the trusted user record. "
            "Reject invalid credentials rather than checking only whether "
            "the password value is non-empty."
        )

    if any(term in text for term in (
        "none", "non-null", "non‑null", "non-string", "attributeerror",
        "input validation",
    )):
        return (
            "Validate the input type and handle None or invalid values "
            "explicitly before calling methods on the input."
        )

    if any(term in text for term in (
        "import time", "module import", "side effect",
    )):
        return (
            "Remove the import-time side effect or move the operation into "
            "a function. Use an if __name__ == '__main__' guard for "
            "code intended to run only when the module is executed directly."
        )

    if any(term in text for term in (
        "docstring", "type hint", "type annotation", "maintainability",
    )):
        return (
            "Add type annotations to function parameters and return values, "
            "and document the function's purpose, inputs, and return value."
        )

    return (
        "Inspect the cited code and evidence, then apply a fix that addresses "
        "the specific behavior described in this finding."
    )


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

        agent_runs: list[dict] = []

        # 1. Logic and Performance Agent
        t0 = time.perf_counter()
        logic_findings = review_logic_performance(pr_context)
        logic_ms = int((time.perf_counter() - t0) * 1000)

        if logic_findings is None:
            logger.error(
                "Logic/Performance agent failed; skipping review publication"
            )
            return

        agent_runs.append({
            "agent_name": "logic_performance",
            "status": "ok",
            "duration_ms": logic_ms,
            "findings_raw": len(logic_findings),
            "findings_kept": len(logic_findings),
        })

        # 2. Security Agent
        security_findings = []
        security_status = "ok"
        security_agent = None
        t0 = time.perf_counter()

        try:
            security_agent = SecurityAgent()
            security_results = security_agent.review(pr_context)

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
            security_status = "error"
            logger.exception(
                "Security Agent failed; continuing with other findings"
            )

        agent_runs.append({
            "agent_name": "security",
            "status": security_status,
            "duration_ms": int((time.perf_counter() - t0) * 1000),
            "findings_raw": getattr(security_agent, "raw_count", len(security_findings)),
            "findings_kept": len(security_findings),
        })

        # 3. Standards Agent
        standards_findings = []
        standards_status = "ok"
        standards_agent = None
        t0 = time.perf_counter()

        try:
            standards_agent = StandardsAgent()
            standards_results = standards_agent.review(pr_context)

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
            standards_status = "error"
            logger.exception(
                "Standards Agent failed; continuing with other findings"
            )

        agent_runs.append({
            "agent_name": "standards",
            "status": standards_status,
            "duration_ms": int((time.perf_counter() - t0) * 1000),
            "findings_raw": getattr(standards_agent, "raw_count", len(standards_findings)),
            "findings_kept": len(standards_findings),
        })

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

        moderated_findings = PersonaAgent.adapt(
            moderated_findings,
            experience_level="mid",
        )

        findings = [
            {
                "agent_type": f.agent_name,
                "severity": f.severity,
                "file": f.file,
                "line": f.line,
                "issue": f.message,
                "recommendation": generate_recommendation(f),
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
            agent_runs=agent_runs,
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