import json
import logging
import re
from groq import Groq

from app.config import settings
from app.ingestion.pr_fetcher import PRContext
from app.rag.retriever import retrieve_context

logger = logging.getLogger("prism.agents.logic_performance")

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a code review agent focused on two things only:
1. Logic correctness -- bugs, edge cases, incorrect conditions, null handling
2. Performance -- inefficient loops, unnecessary queries, obvious complexity issues

You are reviewing a single PR's diff. Focus primarily on lines actually changed
in the diff. You may also flag an issue if the diff's code fails to follow a
pattern or requirement established elsewhere in the retrieved repository
context -- if you do, cite the specific file the requirement comes from.

If you find nothing significant, say so -- don't invent issues.

Respond ONLY with valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "findings": [
    {
      "severity": "high|medium|low",
      "file": "...",
      "issue": "...",
      "recommendation": "..."
    }
  ]
}

If there are no findings, return {"findings": []}.

Additionally, check specifically: does this diff call any function whose
docstring, exception handling, or usage elsewhere in the retrieved context
implies a requirement the diff does not satisfy (a missing parameter, an
unmet precondition)? If so, flag it explicitly and name the file the
requirement comes from.
"""

def _clean_diff_for_query(diff: str, max_chars: int = 500) -> str:
    """Strip git diff boilerplate so the retrieval query is actual
    code content, not headers/path noise."""
    lines = diff.splitlines()
    code_lines = [
        line[1:] for line in lines
        if line.startswith("+") and not line.startswith("+++")
    ]
    return "\n".join(code_lines)[:max_chars]


def review_logic_performance(pr_context: PRContext) -> list[dict] | None:
    """
    Returns a list of findings on success (possibly empty -- that's a
    genuine "no issues found"). Returns None on failure -- a JSON parse
    error or an API/network error -- so callers can distinguish "PRISM
    found nothing" from "PRISM's call broke" instead of conflating them.
    """
    raw_text = ""
    context_block = "No additional repository context retrieved."

    try:
        query_text = _clean_diff_for_query(pr_context.diff)
        retrieved = retrieve_context(pr_context.repo_full_name, query_text, top_k=3)
        if retrieved:
            context_block = "\n\n".join(f"--- {r['file_path']} ---\n{r['text']}" for r in retrieved)
        logger.info("RAG retrieved %d chunk(s): %s", len(retrieved), [r['file_path'] for r in retrieved])
    except Exception:
        logger.exception("RAG retrieval failed -- continuing without repository context")

    try:
        user_prompt = f"""PR Title: {pr_context.title}
Repo: {pr_context.repo_full_name}

Diff:
{pr_context.diff}

Related repository context (for reference only, not part of this PR's changes):
{context_block}
"""
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            max_tokens=8192,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_text = response.choices[0].message.content or ""
        parsed = json.loads(raw_text)
        findings = parsed.get("findings", [])
        logger.info("Logic/performance agent returned %d finding(s)", len(findings))
        return findings

    except json.JSONDecodeError:
        logger.error("Agent response wasn't valid JSON: %s", raw_text[:200])
        return None
    except Exception:
        logger.exception("Logic/performance agent call failed")
        return None