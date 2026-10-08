"""
Shared interface for every review agent (Security, Logic/Performance,
Standards, Persona). Keeping this thin on purpose -- add fields only
once a real agent needs them, don't design this abstractly up front.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.ingestion.pr_fetcher import PRContext


@dataclass
class AgentFinding:
    agent_name: str
    severity: str  # "critical" | "high" | "medium" | "low" | "nitpick"
    message: str
    file: str | None = None
    line: int | None = None
    evidence: list[str] = field(default_factory=list)


class ReviewAgent(ABC):
    name: str = "base"

    @abstractmethod
    def review(self, pr: PRContext) -> list[AgentFinding]:
        """Analyze the PR and return a list of findings."""
        raise NotImplementedError
