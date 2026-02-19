# Compatibility Matrix Contract (v1)

Defines runtime lane classes and merge-blocking behavior for the multi-repo
split:

- `data-contracts` (main contracts/docs/governance project)
- `dc-runner-rust` (required lane)
- `dc-runner-python` (compatibility_non_blocking)
- `dc-runner-php` (compatibility_non_blocking)

## Lane Classes

- `required`: must pass for merge/release.
- `compatibility_non_blocking`: informative compatibility telemetry; does not block merge.

## Current Matrix

- `required`:
  - `rust` (`dc-runner-rust`)
- `compatibility_non_blocking`:
  - `python` (`dc-runner-python`)
  - `php` (`dc-runner-php`)
  - `node` (planned)
  - `c` (planned)

## Guarantees

1. Required lane behavior
- Rust is the canonical required runtime lane for gates and CI verdicts.
- Required lane failures block merge/release.

2. Compatibility lane behavior
- Compatibility lanes run as non-blocking jobs/signals.
- Compatibility failures are reported in artifacts/metrics and must remain visible.
- Compatibility lanes can lag the required lane but must preserve command namespace mapping intent.

3. Lane registration
- Any lane introduced in code/config must be registered in this matrix.
- New non-Rust lanes default to `compatibility_non_blocking`.
- Promotion of a compatibility lane to `required` is an explicit policy/contract change.

4. Certification registry
- Runner certification metadata is canonical in `/specs/schema/runner_certification_registry_v1.yaml`.
- Required lane certification must pass for `rust`.
- Compatibility lane certification results are recorded but non-blocking by default.
- Data Contracts runner execution MUST use pinned release artifacts declared in
  `/specs/schema/dc_runner_rust_lock_v1.yaml`.

## Documentation Contract

- Active docs MUST present Rust-first command examples as canonical.
- Python/PHP examples MAY appear only in clearly labeled compatibility sections marked non-blocking.
- Node/C placeholders may be documented as planned compatibility lanes.
