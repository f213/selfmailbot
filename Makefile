fmt:
	poetry run ruff format src tests
	poetry run ruff check src tests --fix
	poetry run toml-sort pyproject.toml

lint:
	poetry run ruff check src tests
	poetry run mypy src tests
	poetry run toml-sort pyproject.toml --check

dev:
	poetry run watchmedo auto-restart --directory src --patterns '*.py' --recursive -- python -- -m src.app
