.PHONY: help setup test test-cov lint typecheck smoke spec-sync spec-sync-check compat-check runner-spec-sync runner-spec-check transition-gate verify
.DEFAULT_GOAL := help
SOURCE ?=
PYTHON ?= python3

help:
	@printf "\033[1m\033[36mdc-runner-python Make Targets\033[0m\n\n"
	@printf "\033[1m\033[33mCore\033[0m\n"
	@printf "  \033[32m%-18s\033[0m %s\n" "setup" "install dev dependencies"
	@printf "  \033[32m%-18s\033[0m %s\n" "test" "run pytest"
	@printf "  \033[32m%-18s\033[0m %s\n" "test-cov" "run pytest with coverage on refactor modules"
	@printf "  \033[32m%-18s\033[0m %s\n" "lint" "run ruff"
	@printf "  \033[32m%-18s\033[0m %s\n" "typecheck" "run mypy"
	@printf "  \033[32m%-18s\033[0m %s\n" "smoke" "run command surface smoke"
	@printf "  \033[32m%-18s\033[0m %s\n\n" "verify" "test + lint + typecheck + smoke + spec-sync-check + compat-check + runner-spec-check"
	@printf "\033[1m\033[33mSpecs\033[0m\n"
	@printf "  \033[32m%-18s\033[0m %s\n" "spec-sync" "TAG=<upstream-tag> [SOURCE=<path-or-url>] sync pinned upstream specs snapshot"
	@printf "  \033[32m%-18s\033[0m %s\n" "spec-sync-check" "[SOURCE=<path-or-url>] verify upstream lock/snapshot integrity"
	@printf "  \033[32m%-18s\033[0m %s\n" "compat-check" "[SOURCE=<path-or-url>] verify runner compatibility against pinned upstream snapshot"
	@printf "  \033[32m%-18s\033[0m %s\n" "runner-spec-sync" "TAG=<upstream-tag> [SOURCE=<path-or-url>] sync pinned runner-specific specs snapshot"
	@printf "  \033[32m%-18s\033[0m %s\n\n" "runner-spec-check" "[SOURCE=<path-or-url>] verify runner-specific specs lock/snapshot integrity"
	@printf "\033[1m\033[33mTransition\033[0m\n"
	@printf "  \033[32m%-18s\033[0m %s\n" "transition-gate" "full refactor transition checks with rust fallback tie-breaker"

setup:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest || [ $$? -eq 5 ]

test-cov:
	$(PYTHON) -m pytest --cov=spec_runner.cli --cov=spec_runner.governance --cov-fail-under=100

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

transition-gate:
	./scripts/transition_gate.sh

verify: test lint typecheck smoke spec-sync-check compat-check runner-spec-check
