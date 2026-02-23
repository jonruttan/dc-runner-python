# Harness Contract: check

## Status

- v1 harness-dispatched core profile

## Purpose

Execute a harness-dispatched check profile and assert externally visible behavior through
explicitly imported assertion values.

## Required Fields

- `id` (string)
- `harness` (must equal `check`)
- `clauses.profile` (string)
- `clauses` (mapping with `defaults`/`predicates`)

## Contract Import Rules

- `contract.imports` may define default bindings.
- `contract.steps[].imports` may define/override step bindings.
- import entries use list-form `{from, names, as?}` and `from` must be `artifact`.
- Assertions must read values through imported symbols (for example `{var: subject}`).
- `contract.steps[].target` and `contract.steps[].on` are forbidden.

## Type Rules

- runtime setup/config keys are carried under `clauses.config`.
- `clauses.profile` selects runtime profile.
- `clauses.config` carries profile-specific inputs.
- assertions must not depend on implicit runtime bindings.

## Failure Category Guidance

- schema violations -> `schema`
- assertion mismatches -> `assertion`
- runtime/profile faults -> `runtime`
