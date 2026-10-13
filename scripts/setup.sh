#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "-> Edit .env and fill in GITHUB_WEBHOOK_SECRET, GITHUB_API_TOKEN, and an LLM API key before continuing."
fi

echo "Building and starting containers..."
docker-compose up --build -d

echo "Waiting for the API to come up..."
sleep 5
curl -sf http://localhost:8000/health || {
  echo "Health check failed. Run 'docker-compose logs api' to debug."
  exit 1
}

echo ""
echo "PRISM is up. API: http://localhost:8000/health"
echo "Qdrant dashboard: http://localhost:6333/dashboard"
