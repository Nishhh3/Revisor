"""
Build-step 6 target: the Consensus & Decision Layer. Takes the raw
findings from all four agents, dedupes overlapping comments, resolves
conflicts, prioritizes by severity, and produces the final structured
review that actually gets posted to GitHub.

Build this before the agent debate/evidence-sharing layer -- a working
moderator that just concatenates + dedupes is more valuable early than
a debate mechanism with nothing coherent to debate about yet.
"""

from app.agents.base import AgentFinding

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "nitpick": 4}


def moderate(findings: list[AgentFinding]) -> list[AgentFinding]:
    # TODO (build step 6): dedupe findings that point at the same
    # file/line from different agents, then sort by severity.
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))
