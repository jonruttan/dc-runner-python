# Build Tool Command Set Contract (v1)

Defines a tool-agnostic maintenance command contract for runner repositories.

## Scope

This contract standardizes task semantics, not command runners. Implementations
MAY use `cargo xtask`, `make`, `composer`, shell scripts, or equivalent tooling.

## MUST Task IDs

Runner repositories MUST provide deterministic support for:

- `build`
- `test`
- `verify`
- `spec-sync`
- `spec-sync-check`
- `compat-check`

## MAY Task IDs

Runner repositories MAY provide:

- `smoke`
- `package-check`
- `release-verify`
- `docs-check`
- `lint`
- `typecheck`

## Task Semantics

- `build`: compile/build project artifacts required for runner operation.
- `test`: execute implementation test suite used for required lane confidence.
- `verify`: execute canonical local gate sequence for required lane.
- `spec-sync`: update pinned upstream compatibility snapshot and lock metadata.
- `spec-sync-check`: validate pinned snapshot, lock, and manifest consistency.
- `compat-check`: verify runner compatibility surface against pinned upstream contracts.

For MAY tasks, behavior MUST match task-id intent and MUST NOT weaken MUST task
semantics.

## Determinism and Exit Behavior

Task wrappers MUST provide deterministic behavior for required maintenance lane
checks and use stable non-zero failure signaling suitable for CI blocking.

## Manifest Requirement

Each runner repository MUST publish a machine-readable task map manifest at:

- `/specs/impl/<runner>/runner_build_tool_contract_v1.yaml`

The manifest maps task IDs to local invocations and declares supported optional
capabilities.

## Relationship to Runner CLI Contract

This contract is independent of portable runtime CLI contract requirements in:

- `/specs/02_contracts/29_runner_cli_interface.md`
- `/specs/01_schema/runner_cli_contract_v1.yaml`
