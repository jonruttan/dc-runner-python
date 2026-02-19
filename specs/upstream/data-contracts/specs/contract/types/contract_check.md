# Type Contract: contract.check

## Status

- v1 core type

## Purpose

Execute a typed harness check profile and assert externally visible behavior through
explicitly imported assertion values.

## Required Fields

- `id` (string)
- `type` (must equal `contract.check`)
- `harness` (mapping with `check.profile` and `check.config`)
- `contract` (mapping with `defaults`/`steps`)

## Contract Import Rules

- `contract.imports` may define default bindings.
- `contract.steps[].imports` may define/override step bindings.
- import entries use list-form `{from, names, as?}` and `from` must be `artifact`.
- Assertions must read values through imported symbols (for example `{var: subject}`).
- `contract.steps[].target` and `contract.steps[].on` are forbidden.

## Type Rules

- runner-only setup/config keys MUST live under `harness`.
- `harness.check.profile` selects runtime profile.
- `harness.check.config` carries profile-specific inputs.
- assertions must not depend on implicit runtime bindings.

## Failure Category Guidance

- schema violations -> `schema`
- assertion mismatches -> `assertion`
- runtime/profile faults -> `runtime`
