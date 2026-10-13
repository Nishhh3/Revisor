"""
Build-step 5 target. Vulnerability detection, OWASP Top 10, secrets/API
key leaks, dependency risks. Planned tools per the architecture diagram:
Semgrep, Bandit, CodeQL -- run these as static analysis first, then feed
their output to the LLM for triage/explanation rather than relying on
the LLM to spot vulnerabilities unaided.
"""

from app.agents.base import AgentFinding, ReviewAgent
from app.ingestion.pr_fetcher import PRContext


class SecurityAgent(ReviewAgent):
    name = "security"

    def review(self, pr: PRContext) -> list[AgentFinding]:
        raise NotImplementedError("Build after logic_performance_agent works end-to-end.")
