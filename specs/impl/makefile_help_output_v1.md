# Makefile Help Output Formatting (v1)

This repository standardizes `make help` rendering in `Makefile`.

## Required Renderer

The `help` target MUST use an awk renderer with:

- `##@ <Group>` markers for section headings
- `target: ## description` comments for listed targets
- yellow section headings
- green target labels

Canonical renderer shape:

```make
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "}; /^##@/ {printf "\n\033[33m%s\033[0m\n", substr($$0,5)}; /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[32m%-36s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
```

Equivalent awk implementations are allowed if output contract stays the same.

## Output Contract

`make help` MUST render:

- grouped sections from `##@` markers
- one line per documented target
- visible descriptions for every target listed by help
- headings before their grouped targets

Required groups for this repo:

- `Core`
- `Specs`
- `Transition`
- `Aggregate`

Required targets for this repo:

- `help`
- `setup`
- `test`
- `test-cov`
- `lint`
- `typecheck`
- `smoke`
- `spec-sync`
- `spec-sync-check`
- `compat-check`
- `runner-spec-sync`
- `runner-spec-check`
- `transition-gate`
- `verify`

## Scope

- Applies to every `Makefile` in this repository.
- Applies only to `help` rendering and documentation lines.
- Does not change task behavior, flags, or exit semantics.
