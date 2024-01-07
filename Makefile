fmt:
	poetry run ruff format src tests
	poetry run ruff check src tests --fix

lint:
	poetry run ruff check src tests
	poetry run mypy src tests

dev:
	poetry run watchmedo auto-restart --directory src --patterns '*.py' --recursive -- python -- -m src.app
