# Spec-Lang Stdlib Profile v1

This contract defines the complete fixed stdlib surface for spec-lang v1.

## Source Of Truth

- Profile file: `/specs/01_schema/spec_lang_stdlib_profile_v1.yaml`
- The profile is normative for:
  - required symbols
  - category membership
  - declared arity
  - purity/determinism expectations
  - Python/PHP parity requirement

## Requirements

- All profile symbols MUST exist in Python and PHP implementations.
- All profile symbols with declared non-null arity MUST match Python declared arity.
- All profile symbols MUST remain pure and deterministic.
- Each symbol entry MUST define semantic documentation fields for generated references:
  - `summary`
  - `params[]` (`name`, `type`, `description`, `required`)
  - `returns` (`type`, `description`)
  - `errors[]` (`category`, `condition`)
  - `examples[]` (`title`, `expr`, `result`)
  - `since`
- Optional semantic fields:
  - `details`
    - `tags`
- Unknown schema-shape keys for `schema_match` / `schema_errors` MUST fail as `schema`.
- Governance MUST hard-fail on profile/implementation/docs/conformance drift.
- Filesystem utility symbols are pure-only and contract-virtual:
  - `ops.fs.path.*` for POSIX-style path transforms
  - `ops.fs.file.*` for metadata-dict predicates/getters
  - `ops.fs.json.*` for JSON parse and path lookup helpers
  - `ops.fs.glob.*` for deterministic glob pattern matching/filtering

## Schema Shape DSL Keys

Allowed keys:

- `type`
- `required`
- `properties`
- `allow_extra`
- `items`
- `min_items`
- `max_items`
- `min_length`
- `max_length`
- `pattern`
- `const`
- `enum`
- `all_of`
- `any_of`
- `not`
