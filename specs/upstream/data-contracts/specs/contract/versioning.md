# Contract Versioning

Portable contract rules follow a minimal lifecycle model for pre-alpha evolution.

## Version Domains

- **Schema version**: version of the contract-spec schema document (for example
  `/specs/01_schema/schema_v1.md`).
- **Spec-case version pin**: per-case header values in executable
  `yaml contract-spec` blocks:
  - `spec_version`
  - `schema_ref`

Executable cases are valid only when:

- `schema_ref` resolves to an active entry in
  `/specs/01_schema/schema_catalog_v1.yaml`
- `spec_version` equals the schema major referenced by `schema_ref`

## Lifecycle Fields

Each policy rule in `policy_v1.yaml` uses:

- `introduced_in` (required): first contract version where the rule is active.
- `removed_in` (optional): version where the rule is removed.

Version labels use `vN` format (for example `v1`).

## State Model

- Active: `introduced_in` set, no `removed_in`.
- Removed: `introduced_in` + `removed_in`.

## Consistency Rules

- `removed_in` MUST be greater than `introduced_in`.

## Change Policy

Breaking behavior changes MUST include:

- lifecycle field updates in policy
- migration notes in contract/spec docs
- updated traceability and conformance evidence
