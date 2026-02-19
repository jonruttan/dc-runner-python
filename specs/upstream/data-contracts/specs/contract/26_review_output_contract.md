# Review Output Contract (v1)

Source of truth: `/specs/schema/review_snapshot_schema_v1.yaml`

Defines the required machine-consumable markdown shape for active review snapshots under `/docs/reviews/snapshots`.

## Scope

Applies to active review outputs created from prompts in `/docs/reviews/prompts/`.

## Required Metadata

A review snapshot MUST include:

- Date
- Model
- Prompt
- Prompt revision
- Repo revision
- Contract baseline refs
- Runner lane

## Required Section Order

1. `## Scope Notes`
2. `## Command Execution Log`
3. `## Findings`
4. `## Synthesis`
5. `## Spec Candidates (YAML)`
6. `## Classification Labels`
7. `## Reject / Defer List`
8. `## Raw Output`

## Required Table Headers

Command execution log:

- `command | status | exit_code | stdout_stderr_summary`

Findings:

- `Severity | Verified/Hypothesis | File:Line | What | Why | When | Proposed fix`

## Spec Candidate Schema

The `Spec Candidates (YAML)` fenced block MUST parse as a YAML list where each item includes:

- `id`
- `title`
- `type`
- `class`
- `target_area`
- `acceptance_criteria` (non-empty list of strings)
- `affected_paths` (non-empty list of strings)
- `risk`

## Classification Labels

`Classification Labels` MUST include one label per candidate id.

Allowed labels:

- `behavior`
- `docs`
- `tooling`

## Validation Surface

Canonical command:

- `./runners/public/runner_adapter.sh --impl rust review-validate --snapshot <path>`

Exit semantics:

- `0`: snapshot conforms to contract
- `1`: structure/schema violations
- `2`: invalid CLI/config usage
