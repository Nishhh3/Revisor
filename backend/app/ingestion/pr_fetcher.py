"""
Layer 1 of the architecture: PR Data Fetcher.

Responsible for pulling everything the agents need about a single PR:
metadata, unified diff, changed files, and existing comments.

This is intentionally the first real piece of logic to build (step 2
in the build order) -- get this returning real data from a real PR
before writing any agent code.
"""

from dataclasses import dataclass, field

import requests
from github import Github

from app.config import settings


@dataclass
class PRContext:
    repo_full_name: str
    pr_number: int
    title: str = ""
    body: str = ""
    diff: str = ""
    pr_author: str = "" 
    changed_files: list[str] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)


def _fetch_diff_text(repo_full_name: str, pr_number: int) -> str:
    """
    GitHub's PR object only exposes diff_url, not the diff content.
    PyGithub has no built-in helper for this, so we hit the API
    directly with the diff media type.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {settings.github_api_token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def fetch_pr_context(repo_full_name: str, pr_number: int) -> PRContext:
    """
    Fetch PR metadata + diff + changed files via the GitHub API.

    TODO: swap the raw PAT (github_api_token) for a GitHub App
    installation token once the App is registered -- PATs are fine
    for local development only.
    """
    gh = Github(settings.github_api_token)
    repo = gh.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    changed_files = [f.filename for f in pr.get_files()]
    comments = [c.body for c in pr.get_issue_comments()]
    diff_text = _fetch_diff_text(repo_full_name, pr_number)

    return PRContext(
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        title=pr.title,
        body=pr.body or "",
        diff=diff_text,
        changed_files=changed_files,
        comments=comments,
    )