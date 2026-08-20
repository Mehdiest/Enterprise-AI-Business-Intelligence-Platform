# =====================================
# AI Business Intelligence Platform
# =====================================

.PHONY: install install-dev run migrate migrate-down revision \
        docker-build docker-up docker-down docker-logs docker-restart \
        format lint type test test-offline coverage check clean

# --- Dependencies --------------------------------------------------------
install:
	pip install -r requirements/base.txt -r requirements/ai.txt

install-dev:
	pip install -r requirements/all.txt

# --- Run -----------------------------------------------------------------
# NOTE: schema is owned by Alembic. Always `make migrate` before serving a
# fresh database — the app no longer creates tables at runtime.
run:
	uvicorn app.main:app --reload

# --- Database migrations -------------------------------------------------
migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

# Usage: make revision m="add widget table"
revision:
	alembic revision --autogenerate -m "$(m)"

# --- Docker --------------------------------------------------------------
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose down
	docker compose up -d

# --- Quality gates (mirror CI) ------------------------------------------
format:
	black .

lint:
	ruff check .

type:
	mypy app

test:
	pytest

# Migration sanity checks that need no database, Docker, or network.
test-offline:
	python tests/test_migrations_offline.py

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=xml

# Run every static/local gate the way CI does.
check: lint type test

# --- Housekeeping --------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
