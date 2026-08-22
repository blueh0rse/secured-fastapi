.PHONY: up down tests lint db

up:
	docker compose up -d

db:
	docker compose up db -d

down:
	docker compose down -v

tests:
	uv run python -m pytest

lint:
	uv run flake8 app tests
