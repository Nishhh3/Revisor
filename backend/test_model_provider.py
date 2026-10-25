
import json

from app.agents.model_provider import generate

result = generate(
    "Return only JSON.",
    'Return {"status": "ok"}',
    provider="ollama",
)

print(result)
print(json.loads(result))
