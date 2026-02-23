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
- `bundle-sync`
- `bundle-sync-check`
- `compat-check`

## MAY Task IDs

Runner repositories MAY provide:

- `smoke`
- `build-impl`
- `package-impl`
- `package-check`
- `release-verify`
- `docs-check`
- `lint`
- `typecheck`
- `project-scaffold`

## Task Semantics

- `build`: compile/build project artifacts required for runner operation.
- `test`: execute implementation test suite used for required lane confidence.
- `verify`: execute canonical local gate sequence for required lane.
- `bundle-sync`: pull pinned bundle package release assets, verify checksum, and
  materialize resolved lock + file manifest metadata locally.
- `bundle-sync-check`: validate local materialization and lock/manifests against
  pinned bundle package checksum and lock metadata.
- `bundle-sync` and `bundle-sync-check` SHOULD consume root
  `bundles.lock.yaml` (project multi-bundle lock) when available.
- `project-scaffold`: resolve canonical bundle release asset from
  `bundle_id + bundle_version`, verify release sidecar checksum, materialize a
  root `bundles.lock.yaml`, run install/check, and emit scaffold artifacts.
- `build-impl`: compose implementation spec bundle by applying patch overlays to
  a pinned base bundle package.
- `package-impl`: package composed implementation bundle with canonical
  `data-contract-bundle-*` naming and sidecars.
- `compat-check`: verify runner compatibility surface against pinned upstream contracts.

For MAY tasks, behavior MUST match task-id intent and MUST NOT weaken MUST task
semantics.

## Determinism and Exit Behavior

Task wrappers MUST provide deterministic behavior for required maintenance lane
checks and use stable non-zero failure signaling suitable for CI blocking.

## Manifest Requirement

Each runner repository MUST publish a machine-readable task map manifest at:

- `/dc-runner-spec/specs/impl/<runner>/runner_build_tool_contract_v1.yaml`

The manifest maps task IDs to local invocations and declares supported optional
capabilities.

## Relationship to Runner CLI Contract

This contract is independent of portable runtime CLI contract requirements in:

- `/specs/02_contracts/29_runner_cli_interface.md`
- `/specs/01_schema/runner_cli_contract_v1.yaml`
