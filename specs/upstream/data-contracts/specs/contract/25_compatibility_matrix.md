# Compatibility Matrix Contract (v1)

Defines normalized status-evaluation semantics for cross-repo runner telemetry.

## Repository Role

`data-contracts` is a telemetry and governance evaluator.
It is not a runtime-lane executor.

## Lane Classes

- `required`: status failures map to `policy_effect: blocking_fail`.
- `compatibility_non_blocking`: runtime failures remain non-blocking; stale or
  missing telemetry is enforced as control-plane governance breach.

## Matrix Source and Shape

- status producer schema: `/specs/schema/runner_status_report_v1.yaml`
- matrix schema: `/specs/schema/runner_status_matrix_v1.yaml`
- ingest entrypoint: `/scripts/runner_status_ingest.sh`
- registry source: `/specs/schema/runner_certification_registry_v1.yaml`

## Freshness

- compatibility telemetry is stale after 72 hours.
- stale or missing compatibility telemetry for active lanes must fail governance
  in this repository.
- matrix artifacts must still be emitted on partial ingest failure.

## Visibility Guarantees

Matrix output must include, per runner row:

- `runner_id`
- `lane_class`
- `freshness_state` (`fresh|stale|missing`)
- `policy_effect` (`blocking_fail|non_blocking_warn|non_blocking_fail`)

## Promotion Semantics

Promotion between lane classes is an explicit contract/policy change and must be
tracked in registry and governance surfaces.
