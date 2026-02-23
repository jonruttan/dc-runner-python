# Runner Command Entrypoints Contract (v1)

Defines the spec-owned mapping from canonical runner commands to governance
execution profiles.

## Canonical Command Surface

Canonical user-facing commands are:

- `dc-runner governance`
- `dc-runner critical-gate`
- `dc-runner docs-generate-check`
- `dc-runner governance-broad-native`

The mapping source of truth is:

- `/specs/04_governance/runner_entrypoints_v1.yaml`

Schema contract:

- `/specs/01_schema/runner_command_entrypoints_v1.yaml`

## Model

Each command entry defines:

- `id`
- `cli`
- `profile`
- `artifacts[]`
- `exit_codes.allowed[]`

The runner resolves command id to profile and executes the profile from:

- `/specs/governance/check_sets_v1.yaml`

## Hard Requirements

1. `cli` MUST begin with `dc-runner`.
2. `profile` MUST resolve to a defined profile in check sets.
3. Required `artifacts[]` MUST exist on successful/failed command completion.
4. Unknown command ids MUST fail with actionable output listing available ids.
5. Shell scripts are not command-authority sources.
