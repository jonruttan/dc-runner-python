# Subject Profiles Contract (v1)

This contract defines JSON-only subject profile envelopes used by adapters and
harnesses when projecting context/domain data to spec-lang assertions.

## Purpose

- Keep spec-lang evaluator semantics strictly JSON-core and portable.
- Keep implementation/runtime/domain-specific details in adapter projection
  layers.
- Make assertion subjects stable and deterministic across Python/PHP/Rust paths.

## Canonical Envelope

Subject profile values are JSON mappings with this shape:

- `profile_id` (string, required)
- `profile_version` (integer, required)
- `value` (JSON value, required)
- `meta` (JSON mapping, required)
- `context` (JSON mapping, optional)

`value` is the assertion payload.
`meta` provides deterministic descriptor fields for profile consumers.
`context` carries optional normalized facts used for richer assertions.

## Core Rules

- Spec-lang evaluator subjects MUST be JSON values only.
- Subject profile projection MUST be deterministic for equivalent inputs.
- Non-JSON native values (for example Python tuple/PHP runtime internals)
  MUST be represented via JSON projection shape + metadata, not evaluator-native
  value kinds.
- Domain-specific assertion logic SHOULD be library-backed and expressed via
  `evaluate` over projected subjects.

## Context Target

Harnesses MAY provide `context_json` assertion target surfaces for profile
consumers. This is an additive target and does not alter existing targets.

## Related

- `specs/01_schema/subject_profiles_v1.yaml`
- `specs/02_contracts/03_assertions.md`
- `specs/02_contracts/04_harness.md`
- `specs/02_contracts/types/python_profile.md`
- `specs/02_contracts/types/php_profile.md`
- `specs/02_contracts/types/http_profile.md`
- `specs/02_contracts/types/markdown_profile.md`
- `specs/02_contracts/types/makefile_profile.md`
