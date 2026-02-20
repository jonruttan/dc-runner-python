.PHONY: help setup test lint typecheck smoke spec-sync spec-sync-check compat-check runner-spec-sync runner-spec-check verify
.DEFAULT_GOAL := help
SOURCE ?=
PYTHON ?= python3

help:
	@echo "setup      - install dev dependencies"
	@echo "test       - run pytest"
	@echo "lint       - run ruff"
	@echo "typecheck  - run mypy"
	@echo "smoke      - run command surface smoke"
	@echo "spec-sync TAG=<upstream-tag> [SOURCE=<path-or-url>] - sync pinned upstream specs snapshot"
	@echo "spec-sync-check [SOURCE=<path-or-url>] - verify upstream lock/snapshot integrity"
	@echo "compat-check [SOURCE=<path-or-url>] - verify runner compatibility against pinned upstream snapshot"
	@echo "runner-spec-sync TAG=<upstream-tag> [SOURCE=<path-or-url>] - sync pinned runner-specific specs snapshot"
	@echo "runner-spec-check [SOURCE=<path-or-url>] - verify runner-specific specs lock/snapshot integrity"
	@echo "verify     - test + lint + typecheck + smoke + spec-sync-check + compat-check + runner-spec-check"

setup:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest || [ $$? -eq 5 ]

lint:
	$(PYTHON) -m ruff check spec_runner

typecheck:
	$(PYTHON) -m mypy spec_runner

smoke:
	./runner_adapter.sh spec-runner --help

spec-sync:
	@test -n "$(TAG)" || (echo "ERROR: TAG is required (make spec-sync TAG=<upstream-tag>)" >&2; exit 2)
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_data_contracts_specs.sh --tag "$(TAG)" --source "$(SOURCE)"; \
	else \
		./scripts/sync_data_contracts_specs.sh --tag "$(TAG)"; \
	fi

spec-sync-check:
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_data_contracts_specs.sh --check --source "$(SOURCE)"; \
	else \
		./scripts/sync_data_contracts_specs.sh --check; \
	fi

compat-check:
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/verify_upstream_compat.sh --strict --source "$(SOURCE)"; \
	else \
		./scripts/verify_upstream_compat.sh --strict; \
	fi

runner-spec-sync:
	@test -n "$(TAG)" || (echo "ERROR: TAG is required (make runner-spec-sync TAG=<upstream-tag>)" >&2; exit 2)
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_runner_specs.sh --tag "$(TAG)" --source "$(SOURCE)"; \
	else \
		./scripts/sync_runner_specs.sh --tag "$(TAG)"; \
	fi

runner-spec-check:
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/verify_runner_specs.sh --source "$(SOURCE)"; \
	else \
		./scripts/verify_runner_specs.sh; \
	fi

verify: test lint typecheck smoke spec-sync-check compat-check runner-spec-check
