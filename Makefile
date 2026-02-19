.PHONY: help setup test lint typecheck smoke
.DEFAULT_GOAL := help

help:
	@echo "setup      - install dev dependencies"
	@echo "test       - run pytest"
	@echo "lint       - run ruff"
	@echo "typecheck  - run mypy"
	@echo "smoke      - run command surface smoke"

setup:
	python -m pip install -e '.[dev]'

test:
	python -m pytest

lint:
	python -m ruff check spec_runner

typecheck:
	python -m mypy spec_runner

smoke:
	python -m spec_runner.spec_lang_commands --help
