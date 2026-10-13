"""
Build-step 5 target, but its tone-adaptation logic depends on the
Developer Profiler (build step 6). Until that exists, hardcode
experience_level="mid" rather than building profiling logic early.
"""

from app.agents.base import AgentFinding, ReviewAgent
from app.ingestion.pr_fetcher import PRContext


class PersonaAgent(ReviewAgent):
    name = "persona"

    def review(self, pr: PRContext, experience_level: str = "mid") -> list[AgentFinding]:
        # TODO (build step 5): adapt explanation depth/tone based on
        # experience_level ("junior" -> explanatory, "senior" -> concise).
        raise NotImplementedError("Build after the core agent pipeline works.")
