.PHONY: setup test lint format clean

setup:
	uv venv
	. .venv/bin/activate && uv pip install -e .
	. .venv/bin/activate && uv pip install -r requirements-dev.txt

test:
	pytest

lint:
	black .
	isort .
	mypy .

format:
	black .
	isort .

lock:
	uv pip freeze > requirements.lock

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".hypothesis" -exec rm -r {} +