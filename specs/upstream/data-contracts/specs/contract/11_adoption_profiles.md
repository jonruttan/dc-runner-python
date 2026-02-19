# Adoption Profiles Contract (v1)

Defines supported contributor profiles for executing repository checks.

## Profiles

### Core Profile

Command: `make core-check`

Goal:

- fast local confidence on the required lane
- enforce core documentation/spec hygiene

Minimum checks:

- governance spec checks via runner interface (`./scripts/runner_bin.sh governance`)
- style and normalization checks via runner interface (`style-check`, `normalize-check`)
- focused core runner tests via required Rust command surface

### Full Profile

Command: `make check`

Goal:

- pre-merge confidence aligned with required CI gate

Minimum checks:

- all core-profile checks
- required Rust gate bundle (`critical-gate`, `ci-gate-summary`, `test-full`)
- compatibility telemetry lanes (Python/PHP) as non-blocking signals

## Compatibility Matrix Policy

- `rust` is the only required (blocking) runtime lane.
- `python` and `php` are compatibility lanes and non-blocking.
- future non-Rust lanes (`node`, `c`) are compatibility/non-blocking by default.
- Lane class definitions are normative in `/specs/contract/25_compatibility_matrix.md`.

## Compatibility Expectation

- Profile names and command entrypoints are contributor-facing docs contract.
- Implementations SHOULD keep profile wording synchronized in:
  - `README.md`
  - `docs/development.md`
