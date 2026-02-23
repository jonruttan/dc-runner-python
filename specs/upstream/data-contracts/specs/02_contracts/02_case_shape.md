# Case Shape Contract (v1)

## Common Keys

- `spec_version` (required integer)
- `schema_ref` (required absolute virtual-root path)
- `contracts` (required non-empty list)
- `defaults` (optional mapping)
- `domain` (optional)
- `title` (optional)
- `purpose` (optional)

Each `contracts[]` item:

- `id` (required)
- `type` (required directly or inherited from `defaults.type`)
- `clauses` (required mapping)
- `title`/`purpose`/`domain` (optional overrides)
- `harness`/`when`/`expect`/`requires` (optional)

## Source Of Truth

- Machine schema rules are defined in
  `specs/01_schema/registry/v1/*.yaml`.
- Unknown top-level keys are schema errors (hard fail).
- `schema_ref` MUST resolve to an active schema in
  `specs/01_schema/schema_catalog_v1.yaml`.
- `spec_version` MUST match the schema major referenced by `schema_ref`.

## Harness Namespace Rule

Runner-only setup keys MUST live under `harness`.

## Executable Authoring Surface

- Executable contract/spec behavior MUST be authored in `.spec.md` with
  exactly one fenced `yaml contract-spec` block containing one suite mapping.
- This requirement applies to:
  - conformance cases
  - governance cases
  - impl executable cases
  - `type: spec_lang.export` cases under `specs/libraries`

## Type-Specific Fields

Type-specific keys are defined per harness contract and schema docs.
