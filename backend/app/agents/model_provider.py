
import logging

from groq import Groq

from app.config import settings

logger = logging.getLogger("prism.agents.model_provider")


def generate(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0,
    max_tokens: int = 2048,
    provider: str | None = None,
    fallback_to_groq: bool = False,
) -> str:
    """
    Generate text using Groq only.

    provider and fallback_to_groq are retained for compatibility
    with existing callers, but no other provider is used.
    """
    del provider, fallback_to_groq

    api_key = settings.groq_api_key
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    model = getattr(
        settings,
        "groq_model",
        "llama-3.3-70b-versatile",
    )

    client = Groq(
        api_key=api_key,
        timeout=60,
        max_retries=2,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        if not response.choices:
            raise RuntimeError("Groq returned no completion choices")

        message = response.choices[0].message
        content = message.content

        if not isinstance(content, str) or not content.strip():
            refusal = getattr(message, "refusal", None)
            if refusal:
                raise RuntimeError(
                    f"Groq refused the request: {str(refusal)[:200]}"
                )
            raise RuntimeError("Groq returned an empty response")

        return content.strip()

    except Exception:
        logger.exception("Groq model generation failed")
        raise
