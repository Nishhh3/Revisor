
"""
REVISOR consensus layer.

Deduplicates overlapping findings and sorts them by severity.
"""

import re

from app.agents.base import AgentFinding

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "nitpick": 4,
}


def _normalize_message(message: str) -> str:
    """Normalize text for duplicate comparison."""
    return re.sub(r"\W+", " ", message.lower()).strip()


def _dedupe_key(finding: AgentFinding) -> tuple:
    """
    Prefer exact file/line matches. If line numbers are unavailable,
    compare normalized messages within the same file.
    """
    file_path = (finding.file or "").lower().replace("\\", "/")

    if finding.line is not None:
        return file_path, finding.line

    return file_path, _normalize_message(finding.message)


def moderate(findings: list[AgentFinding]) -> list[AgentFinding]:
    """
    Remove overlapping findings, preserve the strongest severity,
    combine evidence, and return findings in severity order.
    """
    merged = {}

    for finding in findings:
        severity = finding.severity.lower()
        if severity not in SEVERITY_ORDER:
            severity = "low"

        key = _dedupe_key(finding)
        existing = merged.get(key)

        if existing is None:
            merged[key] = AgentFinding(
                agent_name=finding.agent_name,
                severity=severity,
                message=finding.message,
                file=finding.file,
                line=finding.line,
                evidence=list(finding.evidence),
            )
            continue

        # Keep the more severe finding.
        if SEVERITY_ORDER[severity] < SEVERITY_ORDER[existing.severity]:
            existing.severity = severity
            existing.message = finding.message
            existing.agent_name = finding.agent_name

        # Preserve distinct evidence from both agents.
        for item in finding.evidence:
            if item not in existing.evidence:
                existing.evidence.append(item)

    return sorted(
        merged.values(),
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            (item.file or "").lower(),
            item.line or 0,
        ),
    )
