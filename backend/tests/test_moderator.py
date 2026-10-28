from app.agents.base import AgentFinding
from app.agents.moderator import moderate


def make_finding(agent, severity, message, line=10, evidence=None):
    return AgentFinding(
        agent_name=agent,
        severity=severity,
        message=message,
        file="example.py",
        line=line,
        evidence=evidence or [],
    )


def test_duplicate_secret_findings_are_merged():
    findings = [
        make_finding(
            "security",
            "high",
            "Hardcoded API key exposes a secret credential",
            evidence=["Secret assignment detected"],
        ),
        make_finding(
            "logic_performance",
            "medium",
            "Hardcoded credential detected; may expose secret",
            evidence=["Credential-like assignment"],
        ),
    ]

    result = moderate(findings)

    assert len(result) == 1
    assert result[0].severity == "high"
    assert len(result[0].evidence) == 2


def test_unrelated_findings_on_same_line_are_preserved():
    findings = [
        make_finding("security", "high", "SQL injection vulnerability"),
        make_finding("standards", "low", "Missing function docstring"),
    ]

    result = moderate(findings)

    assert len(result) == 2


def test_highest_severity_is_preserved():
    findings = [
        make_finding("standards", "low", "Hardcoded secret credential"),
        make_finding("security", "critical", "Hardcoded API key exposes secret"),
    ]

    result = moderate(findings)

    assert len(result) == 1
    assert result[0].severity == "critical"


def test_distinct_evidence_is_merged_without_duplicates():
    findings = [
        make_finding(
            "security",
            "high",
            "Hardcoded API key exposes secret",
            evidence=["Secret assignment detected"],
        ),
        make_finding(
            "standards",
            "low",
            "Hardcoded credential detected; may expose secret",
            evidence=["Secret assignment detected", "Credential stored in source"],
        ),
    ]

    result = moderate(findings)

    assert len(result) == 1
    assert result[0].evidence == [
        "Secret assignment detected",
        "Credential stored in source",
    ]
