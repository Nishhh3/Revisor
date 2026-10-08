"""
Posts agent findings back to the PR as a single comment.

Step 4 in the build order -- closes the loop from "agent produced
findings" to "a human looking at the PR can actually see them."
"""

import logging

from github import Github

from app.config import settings

logger = logging.getLogger("prism.output.pr_commenter")

SEVERITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def format_findings_comment(findings: list[dict]) -> str:
    """
    Turn a list of finding dicts into one Markdown comment body.
    Returns a short "all clear" message if there are no findings.
    """
    if not findings:
        return "**PRISM Review**\n\nNo logic or performance issues found in this PR. ✅"

    lines = ["**PRISM Review** — Logic & Performance\n"]
    for f in findings:
        emoji = SEVERITY_EMOJI.get(f.get("severity", "low"), "⚪")
        lines.append(
            f"{emoji} **{f.get('severity', 'unknown').upper()}** — `{f.get('file', 'unknown file')}`\n"
            f"> {f.get('issue', 'No description provided.')}\n"
            f"> **Suggested fix:** {f.get('recommendation', 'N/A')}\n"
        )
    return "\n".join(lines)


def post_findings_comment(repo_full_name: str, pr_number: int, findings: list[dict]) -> None:
    """
    Post a single comment on the PR summarizing all findings.
    Logs and swallows failures rather than crashing the webhook --
    a failed comment post shouldn't take down event processing.
    """
    try:
        gh = Github(settings.github_api_token)
        repo = gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        body = format_findings_comment(findings)
        pr.create_issue_comment(body)
        logger.info("Posted review comment to %s PR #%d", repo_full_name, pr_number)
    except Exception:
        logger.exception("Failed to post PR comment on %s PR #%d", repo_full_name, pr_number)