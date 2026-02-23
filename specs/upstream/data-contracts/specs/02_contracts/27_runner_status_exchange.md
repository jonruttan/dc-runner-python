# Runner Status Exchange Contract (v1)

Defines the cross-repo status exchange and certification contracts between
`data-contracts` and external runner repositories (`dc-runner-*`).

## Purpose

- Keep `data-contracts` as control-plane for specs/docs/governance.
- Keep runtime implementations external.
- Standardize how runners publish status and how `data-contracts` consumes it.

## Producer Contract (Runner Repos)

Each active runner repository MUST publish a versioned status report artifact
on releases.

Required report schema:

- `/specs/01_schema/runner_status_report_v1.yaml`

Required producer fields:

- `version`
- `runner_id`
- `implementation_repo`
- `release_version`
- `commit_sha`
- `generated_at` (UTC RFC3339)
- `lane_class`
- `overall_status`
- `fresh_until`
- `command_results[]`
- `artifact_refs[]`

Producers MUST ensure:

- status artifact URLs are immutable release asset URLs
- checksums are included in report metadata where supported
- `fresh_until` reflects producer freshness intent

Each active runner repository MUST also emit a runner execution certificate
artifact via `runner-certify`.

Required certificate schema:

- `/specs/01_schema/runner_execution_certificate_v1.yaml`

Required certificate registry:

- `/specs/01_schema/runner_certification_registry_v1.yaml`

Required certificate outputs:

- `/.artifacts/runner-certification-{runner}.json`
- `/.artifacts/runner-certification-{runner}.md`

Required certificate v1 sections:

- `runner`
- `execution_intent`
- `equivalence`
- `summary`
- `checks`
- `proof`

## Consumer Contract (`data-contracts`)

`data-contracts` MUST ingest runner release artifacts and emit a normalized
matrix snapshot.

Required matrix schema:

- `/specs/01_schema/runner_status_matrix_v1.yaml`

Canonical ingest outputs:

- `/.artifacts/runner-status-matrix.json`
- `/.artifacts/runner-status-matrix.md`
- `/.artifacts/runner-status-ingest-log.json`

Canonical ingest entrypoint:

- `/scripts/runner_status_ingest.sh`

Consumer validation rules:

- producer report `version` MUST be compatible with
  `/specs/01_schema/runner_status_report_v1.yaml`
- validation context MUST use control-plane schema pin metadata from
  `/specs/01_schema/schema_catalog_v1.yaml`

## Freshness and Enforcement

- Compatibility lanes remain non-blocking for execution verdicts.
- Compatibility telemetry older than 72 hours is stale.
- Stale or missing compatibility telemetry beyond SLO is a governance policy
  failure.
- Rust required-lane status remains merge-blocking.

## Error Handling

Ingest MUST always emit matrix and ingest log artifacts, including partial
failure conditions.

Common failure classes:

- missing release metadata
- missing status asset
- invalid status report shape
- stale report beyond configured SLO
- checksum mismatch when digest metadata exists

## Non-Goals

- This contract does not move runner implementation code into `data-contracts`.
- This contract does not change lane-class ownership semantics in
  `/specs/02_contracts/25_compatibility_matrix.md`.
