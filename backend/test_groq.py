
from app.agents.model_provider import generate

result = generate(
    system_prompt="Return only valid JSON.",
    user_prompt="Return a JSON object with status set to ok.",
    max_tokens=100,
)

print("Groq response:", result)
