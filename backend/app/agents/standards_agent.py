"""
Build-step 4 target: the first agent to use RAG. Pulls coding
standards, architecture rules, and project conventions from the
Qdrant repository index (see app/core/repo_indexer.py, build step 4)
before calling the LLM.
"""

from app.agents.base import AgentFinding, ReviewAgent
from app.ingestion.pr_fetcher import PRContext


class StandardsAgent(ReviewAgent):
    name = "standards"

    def review(self, pr: PRContext) -> list[AgentFinding]:
        # TODO (build step 4): query Qdrant for relevant docs/ADRs/coding
        # guidelines, inject them into the prompt alongside the diff.
        raise NotImplementedError("Build after the Repository Indexer + Qdrant are wired up.")
