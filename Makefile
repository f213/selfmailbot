fmt:
	poetry run ruff format src tests
	poetry run ruff check src tests --fix

lint:
	poetry run ruff check src tests
	poetry run mypy src tests
