.PHONY: help setup test test-cov lint typecheck smoke spec-sync spec-sync-check compat-check runner-spec-sync runner-spec-check transition-gate verify
.DEFAULT_GOAL := help
SOURCE ?=
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "}; /^##@/ {printf "\n\033[33m%s\033[0m\n", substr($$0,5)}; /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[32m%-36s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Core
setup: ## Install dev dependencies
	$(PYTHON) -m pip install -e '.[dev]'

test: ## Run pytest
	$(PYTHON) -m pytest || [ $$? -eq 5 ]

test-cov: ## Run pytest with coverage on refactor modules
	$(PYTHON) -m pytest --cov=spec_runner.cli --cov=spec_runner.governance --cov-fail-under=100

lint: ## Run ruff
	$(PYTHON) -m ruff check spec_runner

typecheck: ## Run mypy
	$(PYTHON) -m mypy spec_runner

smoke: ## Run command surface smoke
	./runner_adapter.sh spec-runner --help

##@ Specs
spec-sync: ## Sync pinned upstream specs snapshot (TAG required)
	@test -n "$(TAG)" || (echo "ERROR: TAG is required (make spec-sync TAG=<upstream-tag>)" >&2; exit 2)
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_data_contracts_specs.sh --tag "$(TAG)" --source "$(SOURCE)"; \
	else \
		./scripts/sync_data_contracts_specs.sh --tag "$(TAG)"; \
	fi

spec-sync-check: ## Verify upstream lock/snapshot integrity
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_data_contracts_specs.sh --check --source "$(SOURCE)"; \
	else \
		./scripts/sync_data_contracts_specs.sh --check; \
	fi

compat-check: ## Verify runner compatibility against pinned upstream snapshot
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/verify_upstream_compat.sh --strict --source "$(SOURCE)"; \
	else \
		./scripts/verify_upstream_compat.sh --strict; \
	fi

runner-spec-sync: ## Sync pinned runner-specific specs snapshot (TAG required)
	@test -n "$(TAG)" || (echo "ERROR: TAG is required (make runner-spec-sync TAG=<upstream-tag>)" >&2; exit 2)
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/sync_runner_specs.sh --tag "$(TAG)" --source "$(SOURCE)"; \
	else \
		./scripts/sync_runner_specs.sh --tag "$(TAG)"; \
	fi

runner-spec-check: ## Verify runner-specific specs lock/snapshot integrity
	@if [ -n "$(SOURCE)" ]; then \
		./scripts/verify_runner_specs.sh --source "$(SOURCE)"; \
	else \
		./scripts/verify_runner_specs.sh; \
	fi

##@ Transition
transition-gate: ## Run full transition checks with rust fallback tie-breaker
	./scripts/transition_gate.sh

##@ Aggregate
verify: test lint typecheck smoke spec-sync-check compat-check runner-spec-check ## Run blocking local verification suite
