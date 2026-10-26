
"""Adapt code review explanations to the developer's experience level."""

import logging

from app.agents.base import AgentFinding, ReviewAgent
from app.ingestion.pr_fetcher import PRContext

logger = logging.getLogger("prism.agents.persona")

EXPERIENCE_LEVELS = {"junior", "mid", "senior"}


class PersonaAgent(ReviewAgent):
    name = "persona"

    def review(
        self,
        pr: PRContext,
        experience_level: str = "mid",
    ) -> list[AgentFinding]:
        """
        Persona adaptation is applied to existing findings by adapt().
        This method satisfies the common ReviewAgent interface.
        """
        logger.debug(
            "Persona review requested for PR #%s at level %s",
            pr.pr_number,
            experience_level,
        )
        return []

    @staticmethod
    def adapt(
        findings: list[AgentFinding],
        experience_level: str = "mid",
    ) -> list[AgentFinding]:
        """Adapt finding explanations without changing their meaning."""
        level = experience_level.lower()
        if level not in EXPERIENCE_LEVELS:
            level = "mid"

        adapted = []

        for finding in findings:
            message = finding.message

            if level == "junior":
                message = (
                    f"What to look at: {message}\n"
                    "Why it matters: Understand how this issue could affect "
                    "the code's behavior, security, or maintainability, "
                    "then verify the suggested fix with a test."
                )
            elif level == "senior":
                message = f"{message} (Concise review; validate against the code context.)"

            adapted.append(
                AgentFinding(
                    agent_name=finding.agent_name,
                    severity=finding.severity,
                    message=message,
                    file=finding.file,
                    line=finding.line,
                    evidence=list(finding.evidence),
                )
            )

        return adapted
