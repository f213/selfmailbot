fmt:
	poetry run ruff format src
	poetry run ruff check src --fix
	poetry run toml-sort pyproject.toml

lint:
	poetry run ruff check src
	poetry run mypy src
	poetry run toml-sort pyproject.toml --check

dev:
	poetry run watchmedo auto-restart --directory src --patterns '*.py' --recursive -- python -- -m src.app

worker:
	poetry run watchmedo auto-restart --directory src --patterns '*.py' --recursive -- celery -- -A src.celery worker --purge
