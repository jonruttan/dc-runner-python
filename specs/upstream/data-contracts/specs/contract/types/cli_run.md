# Type Contract: cli.run

## Status

- v1 core type

## Purpose

Run a command entrypoint and assert against process outputs.

## Required Fields

- `id` (string)
- `type` (must equal `cli.run`)
- `argv` (list)
- `exit_code` (int)
- `assert` (assertion tree)

## Optional Fields

- `harness` (mapping, runner setup keys only)
- common optional fields from schema v1 (`title`, `assert_health`, `expect`, `requires`)

## Targets

- `stdout`
- `stderr`
- `stdout_path`
- `stdout_path_text`
- `context_json`

## Type Rules

- runner setup keys MUST live under `harness`
- `stdout_path_text` resolves from first non-empty stdout line path
- target semantics:
  - `stdout`/`stderr`: text subjects
  - `stdout_path`: first non-empty stdout line as path text subject
  - `stdout_path.exists`: adapter-provided boolean derived subject for
    existence checks
  - `context_json`: JSON subject profile envelope for `cli.run/v1`

## Failure Category Guidance

- schema violations -> `schema`
- assertion mismatches -> `assertion`
- process/runtime faults -> `runtime`
