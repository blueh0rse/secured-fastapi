.PHONY: up down tests lint

up:
	docker compose up -d

db:
	docker compose up db -d

down:
	docker compose down -v

tests:
	uv run --no-project python -m pytest

lint:
	uv run --no-project flake8 app tests
