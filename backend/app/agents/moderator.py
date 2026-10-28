
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
    """Normalize a finding message for duplicate comparison."""
    return re.sub(r"\W+", " ", (message or "").lower()).strip()


def _issue_family(message: str) -> str:
    """Identify common issue categories across differently worded findings."""
    text = _normalize_message(message)

    patterns = [
        (
            "hardcoded_secret",
            r"\b(hardcoded|hard coded)\b.{0,50}\b(secret|credential|api key|token|password)\b"
            r"|\b(secret|credential|api key|token|password)\b.{0,50}\b(hardcoded|hard coded|embedded)\b",
        ),
        (
            "secret_leak",
            r"\b(print|logging|log|expose|leak|disclose)\b.{0,60}\b(secret|credential|api key|token|password)\b"
            r"|\b(secret|credential|api key|token|password)\b.{0,60}\b(print|logging|log|leak|expose)\b",
        ),
        ("weak_hash", r"\b(md5|sha1|weak hash|cryptographically weak)\b"),
        (
            "import_side_effect",
            r"\b(import time|module import|importing)\b.{0,60}\b(side effect|print|execute|output)\b"
            r"|\b(side effect)\b.{0,60}\b(import|module)\b",
        ),
        (
            "credential_validation",
            r"\b(password|credential|authentication|verify_user)\b.{0,70}\b(validate|verify|check|truthy|match)\b",
        ),
        (
            "input_validation",
            r"\b(null|none|non string|non string|input validation|attributeerror)\b",
        ),
    ]

    for family, pattern in patterns:
        if re.search(pattern, text):
            return family

    return ""



def _dedupe_key(finding: AgentFinding) -> tuple:
    """
    Merge recognized issue families across agents.
    For unrecognized issues, require matching file, line, and
    normalized message so unrelated findings are preserved.
    """
    file_path = (finding.file or "").lower().replace("\\", "/").strip()
    family = _issue_family(finding.message)

    if family:
        return file_path, "family", family

    return (
        file_path,
        "message",
        finding.line,
        _normalize_message(finding.message),
    )



def moderate(findings: list[AgentFinding]) -> list[AgentFinding]:
    """
    Merge likely duplicate findings, preserve the strongest severity,
    combine distinct evidence, and sort by severity.
    """
    merged = {}

    for finding in findings:
        severity = (finding.severity or "low").lower()
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
                evidence=list(finding.evidence or []),
            )
            continue

        # Preserve the strongest severity and its associated explanation.
        if SEVERITY_ORDER[severity] < SEVERITY_ORDER[existing.severity]:
            existing.severity = severity
            existing.message = finding.message
            existing.agent_name = finding.agent_name

        # Keep a known line number when the original finding lacks one.
        if existing.line is None and finding.line is not None:
            existing.line = finding.line

        # Preserve evidence from all agents without exact duplicates.
        for item in finding.evidence or []:
            if item not in existing.evidence:
                existing.evidence.append(item)

        # Retain attribution to all agents that contributed to the finding.
        agents = getattr(existing, "contributing_agents", None)
        if agents is None:
            agents = [existing.agent_name]
            existing.contributing_agents = agents

        if finding.agent_name not in agents:
            agents.append(finding.agent_name)

    return sorted(
        merged.values(),
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            (item.file or "").lower(),
            item.line or 0,
        ),
    )
