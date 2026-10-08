import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings
from app.ingestion.pr_fetcher import fetch_pr_context

from app.agents.logic_performance_agent import review_logic_performance
from app.output.pr_commenter import post_findings_comment
from app.models.review_store import save_review

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


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
):
    body = await request.body()
    verify_signature(body, x_hub_signature_256)

    payload = await request.json()
    action = payload.get("action")

    logger.info("Received GitHub event=%s action=%s", x_github_event, action)

    if x_github_event == "pull_request" and action in {"opened", "synchronize", "reopened"}:
        pr_number = payload["pull_request"]["number"]
        repo_full_name = payload["repository"]["full_name"]
        logger.info("PR event queued: repo=%s pr=%s action=%s", repo_full_name, pr_number, action)

        # NOTE: this is a blocking network call running inline on the event loop.
        # Fine for solo dev testing against one PR at a time. This is exactly
        # what step 6 (Celery) fixes -- don't "solve" it here, just be aware
        # a slow GitHub API response currently stalls the whole server.
        pr_context = fetch_pr_context(repo_full_name, pr_number)

        logger.info(
            "Fetched PR context: title=%r files=%d diff_chars=%d",
            pr_context.title,
            len(pr_context.changed_files),
            len(pr_context.diff),
        )

        findings = review_logic_performance(pr_context)

        if findings is None:
            logger.error("Agent call failed -- skipping comment post, this is not a genuine clean review")
        else:
            for f in findings:
                logger.info("Finding: [%s] %s -- %s", f.get("severity"), f.get("file"), f.get("issue"))

            review_id = save_review(repo_full_name, pr_number, pr_context.title, pr_context.pr_author, findings)
            logger.info("Saved review %s to database", review_id)

            post_findings_comment(repo_full_name, pr_number, findings)

    return {"received": True}