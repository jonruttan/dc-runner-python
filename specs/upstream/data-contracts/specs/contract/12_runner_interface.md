# Runner Interface Contract (v1)

Defines the implementation-agnostic boundary between runner repositories and the
`data-contracts` control plane.

## Scope

This repository does not execute runner implementation lanes in canonical CI.
Runtime execution ownership lives in runner repositories:

- `dc-runner-rust`
- `dc-runner-python`
- `dc-runner-php`

`data-contracts` owns:

- contract/schema definitions for status exchange
- compatibility matrix normalization rules
- governance rules for freshness and visibility
- docs and reference integrity
- runner-ingestible pack manifests under `/specs/packs/`
- portable runner CLI contract definitions

## Stable Boundary

The public command boundary remains:

- `scripts/runner_bin.sh`

This boundary is retained for compatibility, but control-plane CI in this repo
must not depend on runtime-lane execution through that boundary.

## Status Exchange Boundary

Runner repositories publish release assets that conform to:

- `/specs/01_schema/runner_status_report_v1.yaml`

The control plane ingests and normalizes status through:

- `/scripts/runner_status_ingest.sh`
- `/specs/01_schema/runner_status_matrix_v1.yaml`
- `/specs/02_contracts/25_compatibility_matrix.md`
- `/specs/02_contracts/27_runner_status_exchange.md`

Portable CLI surface is defined by:

- `/specs/02_contracts/29_runner_cli_interface.md`
- `/specs/01_schema/runner_cli_contract_v1.yaml`

## Policy Semantics

- `lane_class: required` indicates blocking policy effect when the required lane
  report fails or is unavailable.
- `lane_class: compatibility_non_blocking` indicates non-blocking runtime
  compatibility semantics.
- Compatibility telemetry freshness is enforced at 72 hours in this repository.

## Forbidden Couplings

`data-contracts` MUST NOT:

- vendor local runner implementation code
- execute implementation-specific runtime suites in canonical CI
- treat compatibility-lane execution as merge-blocking runtime ownership in this
  repository
