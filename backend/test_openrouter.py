
import json

from app.agents.model_provider import generate

result = generate(
    system_prompt="Return only a JSON object.",
    user_prompt='Return exactly this JSON: {"status": "ok"}',
    provider="openrouter",
    max_tokens=100,
)

print(result)
print("Valid JSON:", isinstance(json.loads(result), dict))
