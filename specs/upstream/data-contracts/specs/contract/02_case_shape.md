# Case Shape Contract (v1)

## Common Keys

- `id` (required)
- `type` (required)
- `title` (optional)
- `harness` (optional mapping)
- `assert_health` (optional mapping)

## Source Of Truth

- Machine schema rules are defined in
  `specs/schema/registry/v1/*.yaml`.
- Unknown top-level keys are schema errors (hard fail).

## Harness Namespace Rule

Runner-only setup keys MUST live under `harness`.

## Executable Authoring Surface

- Executable contract/spec behavior MUST be authored in `.spec.md` with
  fenced `yaml contract-spec` blocks.
- This requirement applies to:
  - conformance cases
  - governance cases
  - impl executable cases
  - `type: spec_lang.export` cases under `specs/libraries`

## Type-Specific Fields

Type-specific keys are defined per harness contract and schema docs.

## Assertion Health Policy Override

- `assert_health.mode` MAY be provided per case.
- Allowed values: `ignore`, `warn`, `error`.
