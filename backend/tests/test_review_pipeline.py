
from unittest.mock import patch

from app.agents.base import AgentFinding
from app.ingestion.pr_fetcher import PRContext
from app.api import webhooks


def test_review_pipeline_without_external_side_effects():
    pr = PRContext(
        repo_full_name="example/repo",
        pr_number=1,
        title="Test PR",
        pr_author="tester",
        diff="diff --git a/example.py b/example.py",
        changed_files=["example.py"],
    )

    logic_result = [
        {
            "agent_type": "logic_performance",
            "severity": "high",
            "file": "example.py",
            "line": 1,
            "issue": "Test logic issue",
            "recommendation": "Fix the logic",
            "evidence": ["test evidence"],
        }
    ]

    security_result = [
        AgentFinding(
            agent_name="security",
            severity="medium",
            message="Test security issue",
            file="example.py",
            line=2,
            evidence=["security evidence"],
        )
    ]

    standards_result = [
        AgentFinding(
            agent_name="standards",
            severity="low",
            message="Test maintainability issue",
            file="example.py",
            line=3,
            evidence=["standards evidence"],
        )
    ]

    with (
        patch.object(webhooks, "fetch_pr_context", return_value=pr),
        patch.object(webhooks, "review_logic_performance", return_value=logic_result),
        patch.object(webhooks.SecurityAgent, "review", return_value=security_result),
        patch.object(webhooks.StandardsAgent, "review", return_value=standards_result),
        patch.object(webhooks, "save_review", return_value="test-review-id") as save,
        patch.object(webhooks, "post_findings_comment") as comment,
    ):
        webhooks.run_review("example/repo", 1)

    save.assert_called_once()
    comment.assert_called_once()

    posted_findings = comment.call_args.args[2]
    agents = {finding["agent_type"] for finding in posted_findings}

    assert {"logic_performance", "security", "standards"}.issubset(agents)
