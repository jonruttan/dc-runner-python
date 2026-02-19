# Contract Versioning

Portable contract rules follow lifecycle states to support safe evolution.

## Lifecycle Fields

Each policy rule in `policy-v1.yaml` uses:

- `introduced_in` (required): first contract version where the rule is active.
- `deprecated_in` (optional): version where the rule is deprecated.
- `removed_in` (optional): version where the rule is removed.

Version labels use `vN` format (for example `v1`).

## State Model

- Active: `introduced_in` set, no `deprecated_in`, no `removed_in`.
- Deprecated: `introduced_in` + `deprecated_in`, no `removed_in`.
- Removed: `introduced_in` + `deprecated_in` + `removed_in`.

## Consistency Rules

- `removed_in` MUST NOT be set without `deprecated_in`.
- `deprecated_in` MUST be greater than or equal to `introduced_in`.
- `removed_in` MUST be strictly greater than `deprecated_in`.
- `removed_in` MUST be greater than `introduced_in`.

## Change Policy

Breaking behavior changes MUST include:

- lifecycle field updates in policy
- migration notes in contract/spec docs
- updated traceability and conformance evidence
