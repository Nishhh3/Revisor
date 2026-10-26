
"""
Revisor evaluation harness.

Run from backend/:
    python eval/run_eval.py
    python eval/run_eval.py --no-rag
    python eval/run_eval.py --runs 3
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.logic_performance_agent import review_logic_performance
from app.ingestion.pr_fetcher import PRContext


CASES_DIR = Path(__file__).parent / "cases"
GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"
RESULTS_PATH = Path(__file__).parent / "results.json"

RAG_ON_REPO = "Nishhh3/Revisor-Testing"
CALL_DELAY_SECONDS = 8


# Each pattern identifies a specific expected issue.
# These rules are explicit heuristics, not semantic proof.
MATCH_PATTERNS = {
    "case_01_order_processor.py": [
        r"mutable default|shared state|cart\s*=\s*\[\]",
        r"o\(n\s*\^?\s*2\)|quadratic|list membership|membership check|seen list",
        r"bare except|broad exception|catches all exceptions|"
        r"catch(?:es|ing)? all exceptions|hiding.*exception|"
        r"masks?.*(?:underlying )?errors?|suppresses?.*errors?|"
        r"exception details",
        r"float|decimal|rounding|monetary precision|money math|financial precision|currency precision",
    ],
    "case_02_buggy_basic.py": [
        r"assignment operator|syntax error|instead of.*==|instead of.*comparison",
        r"empty.*scores|empty input|division by zero|zerodivisionerror",
    ],
    "case_03_clean_validator.py": [
        r"validate_password|password.*(?:none|non.string|typeerror|type guard)",
        r"email_pattern|email regex|regex.*subdomain|subdomain|multi.level domain",
    ],
    "case_04_pagination_offby1.py": [
        r"paginate|off.by.one|1.indexed|skipping the first|first page_size",
        r"total_pages|floor division|ceiling division|undercount.*pages",
    ],
    "case_05_clean_math.py": [],
}


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


def run_case(
    case_file: Path,
    repo_full_name: str,
    use_rag: bool = True,
) -> list[dict] | None:
    content = case_file.read_text(encoding="utf-8")
    context = PRContext(
        repo_full_name=repo_full_name,
        pr_number=0,
        title=f"Eval case: {case_file.name}",
        diff=_file_to_diff(case_file.name, content),
        pr_author="eval-harness",
        changed_files=[case_file.name],
    )
    return review_logic_performance(context, use_rag=use_rag)


def _expected_findings(case_data: dict) -> list:
    result = case_data.get("expected_findings")
    if result is None:
        result = case_data.get("expected", [])
    return result if isinstance(result, list) else []


def _finding_text(finding: dict) -> str:
    return " ".join(
        str(finding.get(key, ""))
        for key in ("issue", "recommendation", "category")
    ).lower()


def _score_run(
    case_name: str,
    expected: list[dict],
    actual: list[dict],
) -> dict:
    patterns = MATCH_PATTERNS.get(case_name, [])
    matched_expected = set()
    matched_actual = set()
    matches = []

    for expected_index, expected_item in enumerate(expected):
        if expected_index >= len(patterns):
            continue

        pattern = patterns[expected_index]

        for actual_index, actual_item in enumerate(actual):
            if actual_index in matched_actual:
                continue

            if re.search(pattern, _finding_text(actual_item), re.IGNORECASE):
                matched_expected.add(expected_index)
                matched_actual.add(actual_index)

                expected_severity = str(
                    expected_item.get("severity", "")
                ).lower()
                actual_severity = str(
                    actual_item.get("severity", "")
                ).lower()

                matches.append({
                    "expected": expected_item,
                    "actual": actual_item,
                    "severity_match": (
                        expected_severity == actual_severity
                    ),
                })
                break

    missed = [
        item for index, item in enumerate(expected)
        if index not in matched_expected
    ]
    extra = [
        item for index, item in enumerate(actual)
        if index not in matched_actual
    ]

    tp = len(matches)
    fp = len(extra)
    fn = len(missed)

    precision = tp / (tp + fp) if tp + fp else (
        1.0 if fn == 0 else 0.0
    )
    recall = tp / (tp + fn) if tp + fn else (
        1.0 if fp == 0 else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    severity_matches = sum(
        match["severity_match"] for match in matches
    )

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "severity_agreement": round(
            severity_matches / tp, 4
        ) if tp else None,
        "matched_findings": matches,
        "missed_findings": missed,
        "extra_findings": extra,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-rag", action="store_true",
                        help="Disable repository retrieval entirely")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument(
        "--results",
        type=Path,
        default=RESULTS_PATH,
        help="Output JSON path (defaults to eval/results.json)",
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")

    ground_truth = json.loads(
        GROUND_TRUTH_PATH.read_text(encoding="utf-8")
    )
    repo = RAG_ON_REPO
    results_path = args.results

    all_results = {}
    total_ok = 0
    total_failed = 0
    aggregate_tp = 0
    aggregate_fp = 0
    aggregate_fn = 0
    severity_matches = 0
    severity_total = 0

    for case_file in sorted(CASES_DIR.glob("*.py")):
        case_name = case_file.name
        expected = _expected_findings(
            ground_truth.get(case_name, {})
        )

        print(
            f"\n{'=' * 70}\n"
            f"{case_name} (expected {len(expected)} finding(s))\n"
            f"{'=' * 70}"
        )

        case_runs = []

        for run_number in range(1, args.runs + 1):
            started = time.perf_counter()

            try:
                findings = run_case(
                    case_file,
                    repo,
                    use_rag=not args.no_rag,
                )
                elapsed = round(time.perf_counter() - started, 2)

                if findings is None:
                    record = {
                        "status": "failed",
                        "error": (
                            "Agent returned None. Inspect agent logs "
                            "for provider or parsing details."
                        ),
                        "duration_seconds": elapsed,
                    }
                    total_failed += 1
                    print(f"Run {run_number}: FAILED ({elapsed}s)")
                else:
                    metrics = _score_run(
                        case_name, expected, findings
                    )
                    record = {
                        "status": "ok",
                        "findings": findings,
                        "finding_count": len(findings),
                        "duration_seconds": elapsed,
                        "metrics": metrics,
                    }
                    total_ok += 1
                    aggregate_tp += metrics["true_positives"]
                    aggregate_fp += metrics["false_positives"]
                    aggregate_fn += metrics["false_negatives"]

                    if metrics["severity_agreement"] is not None:
                        severity_matches += sum(
                            item["severity_match"]
                            for item in metrics["matched_findings"]
                        )
                        severity_total += metrics["true_positives"]

                    print(
                        f"Run {run_number}: "
                        f"TP={metrics['true_positives']} "
                        f"FP={metrics['false_positives']} "
                        f"FN={metrics['false_negatives']} "
                        f"Precision={metrics['precision']:.2f} "
                        f"Recall={metrics['recall']:.2f} "
                        f"F1={metrics['f1']:.2f}"
                    )
                    for item in metrics["missed_findings"]:
                        print("  MISSED:", item.get("description", item))
                    for item in metrics["extra_findings"]:
                        print(
                            "  EXTRA:",
                            item.get("issue", item),
                        )

            except Exception as exc:
                elapsed = round(time.perf_counter() - started, 2)
                logging.exception(
                    "Evaluation failed for %s, run %d",
                    case_name, run_number,
                )
                record = {
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {str(exc)[:250]}",
                    "duration_seconds": elapsed,
                }
                total_failed += 1
                print(f"Run {run_number}: FAILED - {record['error']}")

            case_runs.append(record)

            if run_number < args.runs:
                time.sleep(CALL_DELAY_SECONDS)

        all_results[case_name] = {
            "expected": expected,
            "runs": case_runs,
        }

    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    total = total_ok + total_failed
    precision = (
        aggregate_tp / (aggregate_tp + aggregate_fp)
        if aggregate_tp + aggregate_fp else 0.0
    )
    recall = (
        aggregate_tp / (aggregate_tp + aggregate_fn)
        if aggregate_tp + aggregate_fn else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    print(f"\n{'=' * 70}\nOVERALL EVALUATION\n{'=' * 70}")
    print(f"Successful runs:    {total_ok}")
    print(f"Failed runs:        {total_failed}")
    print(f"Failure rate:       {total_failed / total:.2%}" if total else "Failure rate: N/A")
    print(f"Precision:          {precision:.2%}")
    print(f"Recall:             {recall:.2%}")
    print(f"F1 score:           {f1:.2%}")
    print(
        "Severity agreement: "
        f"{severity_matches / severity_total:.2%}"
        if severity_total else "Severity agreement: N/A"
    )
    print(f"Results saved to: {results_path}")
    print(
        "\nNote: Matching uses explicit text patterns. Review matched, "
        "missed, and extra findings before treating these metrics "
        "as authoritative."
    )


if __name__ == "__main__":
    main()
