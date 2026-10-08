"""
Evaluation harness -- feeds each labeled case through the real agent
pipeline (same function running in production), with no GitHub
involved. Supports repeated runs to measure non-determinism, and a
RAG on/off toggle via which repo name is passed.

Usage (run from backend/):
    python eval/run_eval.py
    python eval/run_eval.py --no-rag
    python eval/run_eval.py --runs 3
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)  # without this, RAG's "retrieved N chunk(s)" lines are silently swallowed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.logic_performance_agent import review_logic_performance
from app.ingestion.pr_fetcher import PRContext


CASES_DIR = Path(__file__).parent / "cases"
GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"
RESULTS_PATH = Path(__file__).parent / "results.json"

RAG_ON_REPO = "Nikkk31/check"
RAG_OFF_REPO = "eval/no-such-repo"

CALL_DELAY_SECONDS = 8  # stay under Groq's free-tier TPM cap across back-to-back calls


def _file_to_diff(file_path: str, content: str) -> str:
    lines = content.splitlines()
    diff_lines = [
        f"diff --git a/{file_path} b/{file_path}",
        "new file mode 100644",
        "--- /dev/null",
        f"+++ b/{file_path}",
        f"@@ -0,0 +1,{len(lines)} @@",
    ]
    diff_lines.extend(f"+{line}" for line in lines)
    return "\n".join(diff_lines)


def run_case(case_file: Path, repo_full_name: str) -> list[dict] | None:
    content = case_file.read_text(encoding="utf-8")
    pr_context = PRContext(
        repo_full_name=repo_full_name,
        pr_number=0,
        title=f"Eval case: {case_file.name}",
        diff=_file_to_diff(case_file.name, content),
        pr_author="eval-harness",
        changed_files=[case_file.name],
    )
    return review_logic_performance(pr_context)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-rag", action="store_true")
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    repo = RAG_OFF_REPO if args.no_rag else RAG_ON_REPO
    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text())

    all_results = {}
    for case_file in sorted(CASES_DIR.glob("*.py")):
        expected = ground_truth.get(case_file.name, {}).get("expected_findings", [])
        print(f"\n{'='*70}\n{case_file.name}  (expected {len(expected)} finding(s))\n{'='*70}")

        case_runs = []
        for run_num in range(1, args.runs + 1):
            findings = run_case(case_file, repo)
            if findings is None:
                case_runs.append({"status": "failed"})
                print(f"\n-- Run {run_num}: FAILED (agent call error, not a real result) --")
            else:
                case_runs.append({"status": "ok", "findings": findings})
                print(f"\n-- Run {run_num}: {len(findings)} finding(s) --")
                for f in findings:
                    print(f"  [{f.get('severity','?')}] {f.get('issue','')}")
            time.sleep(CALL_DELAY_SECONDS)

        all_results[case_file.name] = {"expected": expected, "runs": case_runs}

    RESULTS_PATH.write_text(json.dumps(all_results, indent=2))
    print(f"\n\nSaved full results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()