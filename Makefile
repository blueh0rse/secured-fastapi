.PHONY: up down tests lint db

# === run ===

up:
	docker compose up -d

db:
	docker compose up db -d

down:
	docker compose down -v

# === dev ===

tests:
	uv run python -m pytest

lint:
	uv run flake8 --exclude=.venv

install-hooks:
	uv run pre-commit install

# === security ===

secret-scan:
	docker run -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app -v

generate-secret-baseline:
	docker run -u $$(id -u):$$(id -g) -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app --report-path /app/gitleaks-baseline.json --redact

secret-scan-baseline:
	docker run -v $$(pwd):/app ghcr.io/gitleaks/gitleaks:v8.30.1 git /app -v -b /app/gitleaks-baseline.json
