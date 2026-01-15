.PHONY: install test lint format demo clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

demo:
	python examples/demo_scenario_a.py
	@echo "\n---\n"
	python examples/demo_scenario_b.py

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
