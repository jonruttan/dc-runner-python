# Rust-Primary Transition Contract (v1)

Defines the contract for operating this repository with a Rust-primary runner
path while preserving schema/contract behavior guarantees.

Rust-first policy is normative for required gate behavior.

## Intent

- Rust adapter is the required operational runner boundary.
- Python/PHP implementations are supported as non-blocking compatibility lanes.
- Gate/policy behavior remains deterministic with Rust as merge-blocking lane.

## Required Rust-Primary Guarantees

1. CI Rust required lane
- CI MUST exercise core gate commands through the public runner entrypoint
  (`SPEC_RUNNER_BIN=./runners/public/runner_adapter.sh`) with rust mode.
- Rust required lane failures block merge/release.

2. No Python-hardcoded gate dependency
- Gate scripts MUST use runner-interface boundaries instead of direct Python
  script entrypoints, including `ci-gate-summary` orchestration.
- Rust adapter/CLI paths MUST avoid transitive Python delegation.

3. Runner-interface stability under Rust primary
- Required runner-interface subcommands and exit-code contracts MUST remain
  stable for Rust mode.

4. Compatibility lanes are non-blocking
- Python/PHP compatibility jobs may fail without blocking merge.
- Compatibility results MUST be published as artifacts/metrics.

5. Future lane onboarding
- New non-Rust lanes default to non-blocking compatibility class.
- Planned lanes `node` and `c` follow the same policy unless explicitly promoted.

## Adoption and Scope

- Active docs MUST present Rust-first examples as canonical interface path.
- Compatibility examples for Python/PHP MAY appear only in explicit non-blocking
  compatibility sections.
- Adding/removing required runtime support targets is governed by:
  - `specs/contract/08_v1_scope.md`
  - `specs/contract/13_runtime_scope.md`
  - `specs/contract/25_compatibility_matrix.md`

## Non-Goals

- This contract does not remove Python/PHP implementations.
- This contract does not alter assertion/schema semantics.
