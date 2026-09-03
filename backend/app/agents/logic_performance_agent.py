"""
Logic + Performance Agent -- step 3 in the build order.

Takes a PRContext (diff + metadata) and asks the LLM to reason about
correctness and performance issues in the changed code. Returns
structured findings the moderator agent can later merge with
security/standards findings.
"""

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
in the diff. If you find nothing significant, say so -- don't invent issues.

Respond ONLY with valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "findings": [
    {"severity": "high|medium|low", "file": "...", "issue": "...", "recommendation": "..."}
  ]
}
If there are no findings, return {"findings": []}.
"""


def review_logic_performance(pr_context: PRContext) -> list[dict]:
    """
    Send the PR diff to Groq's hosted LLM and get back structured
    logic/performance findings. Returns a list of finding dicts (empty
    list if none, or if the call fails -- we log the failure but don't
    crash the webhook).
    """
    user_prompt = f"""PR Title: {pr_context.title}
Repo: {pr_context.repo_full_name}

Diff:
{pr_context.diff}
"""
    raw_text = ""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=4096,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_text = response.choices[0].message.content
        parsed = json.loads(raw_text)
        findings = parsed.get("findings", [])
        logger.info("Logic/performance agent returned %d finding(s)", len(findings))
        return findings

    except json.JSONDecodeError:
        logger.error("Agent response wasn't valid JSON: %s", raw_text[:200])
        return []
    except Exception:
        logger.exception("Logic/performance agent call failed")
        return []