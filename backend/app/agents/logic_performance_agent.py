import json
import logging

from groq import Groq

from app.config import settings
from app.ingestion.pr_fetcher import PRContext

logger = logging.getLogger("prism.agents.logic_performance")

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a code review agent focused on two things only:
1. Logic correctness -- bugs, edge cases, incorrect conditions, null handling
2. Performance -- inefficient loops, unnecessary queries, obvious complexity issues

You are reviewing a single PR's diff. Only comment on lines actually changed
in the diff. Use the related repository context only to better understand the
changed code; do not report issues on unchanged context alone.

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
"""


def review_logic_performance(pr_context: PRContext) -> list[dict]:
    """
    Review a PR diff for logic correctness and performance issues.

    Returns a list of finding dictionaries. Failures are logged and
    return an empty list so the webhook pipeline does not crash.
    """

    from app.rag.retriever import retrieve_context

    raw_text = ""

    try:
        # Retrieve relevant repository context
        retrieved = retrieve_context(pr_context.repo_full_name, pr_context.diff[:500], top_k=3)
        context_block = "\n\n".join(f"--- {r['file_path']} ---\n{r['text']}" for r in retrieved) or "No additional repository context retrieved."
        logger.info("RAG retrieved %d chunk(s): %s", len(retrieved), [r['file_path'] for r in retrieved])
        
        user_prompt = f"""PR Title: {pr_context.title}
Repo: {pr_context.repo_full_name}

Diff:
{pr_context.diff}

Related repository context (for reference only, not part of this PR's changes):
{context_block}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=4096,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = response.choices[0].message.content or ""

        parsed = json.loads(raw_text)
        findings = parsed.get("findings", [])

        logger.info(
            "Logic/performance agent returned %d finding(s)",
            len(findings),
        )

        return findings

    except json.JSONDecodeError:
        logger.error(
            "Agent response wasn't valid JSON: %s",
            raw_text[:200],
        )
        return []

    except Exception:
        logger.exception("Logic/performance agent call failed")
        return []