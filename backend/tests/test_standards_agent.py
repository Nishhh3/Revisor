from types import SimpleNamespace
import pytest

from app.agents import standards_agent as sa

DIFF = """diff --git a/x.py b/x.py
--- a/x.py
+++ b/x.py
@@ -0,0 +1,3 @@
+def f(a):
+    return a
+# Trigger a fresh webhook event.
"""


def _pr():
    return SimpleNamespace(
        title="t", body="", diff=DIFF, changed_files=["x.py"]
    )


def _run(monkeypatch, findings):
    import json

    monkeypatch.setattr(
        sa, "generate", lambda **kw: json.dumps({"findings": findings})
    )
    return sa.StandardsAgent().review(_pr())


def test_added_lines_parsed():
    assert sa._added_lines(DIFF)["x.py"] == {1, 2, 3}


def test_noise_dropped(monkeypatch):
    out = _run(monkeypatch, [
        {"severity": "low", "file": "x.py", "line": 1,
         "message": "Function f is missing a docstring", "evidence": []},
        {"severity": "nitpick", "file": "x.py", "line": 3,
         "message": "Standalone comment is not attached to code", "evidence": []},
    ])
    assert out == []


def test_line_outside_diff_dropped(monkeypatch):
    out = _run(monkeypatch, [
        {"severity": "medium", "file": "x.py", "line": 99,
         "message": "Duplicated logic should be consolidated", "evidence": []},
    ])
    assert out == []


def test_valid_finding_kept(monkeypatch):
    out = _run(monkeypatch, [
        {"severity": "medium", "file": "x.py", "line": 2,
         "message": "Duplicated logic should be consolidated", "evidence": ["a"]},
    ])
    assert len(out) == 1 and out[0].severity == "medium" and out[0].line == 2

@pytest.mark.parametrize("msg", [
    "Functions lack docstrings or type hints, reducing readability",
    "Placeholder comment is not accompanied by implementation, suggesting dead or incomplete code",
    "File does not end with a newline character",
    "Use of MD5 for hashing may be inappropriate; consider a stronger hash",
])
def test_known_noise_dropped(msg):
    assert sa._is_noise(msg)


def test_real_finding_not_noise():
    assert not sa._is_noise("Duplicated validation logic in two handlers should be consolidated")
