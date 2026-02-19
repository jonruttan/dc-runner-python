# Contract Versioning

Portable contract rules follow a minimal lifecycle model for pre-alpha evolution.

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
