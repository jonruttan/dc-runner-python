# Spec-Lang Libraries Contract (v1)

## Purpose

Provide portable, reusable spec-lang function libraries shared across cases
without host-language hooks.

## Harness Shape

Cases MAY configure library loading via `harness.spec_lang`:

- `includes` (list[string]): ordered paths to library spec docs/files
- `exports` (list[string], optional): explicit symbol allowlist visible to case
- `imports` (list[mapping], optional): case-scoped stdlib import bindings
  (`from`, `names`, optional `as`)

Governance policy reuse:

- `type: governance.check` cases MUST load library symbols through
  `harness.chain` library-symbol exports/imports and MUST call exported
  library symbols from `evaluate`.

Library paths:

- use virtual-root path semantics (`/` = contract root)
- root-relative values normalize to canonical `/...`
- MUST resolve within contract root
- MUST point to existing files
- MAY reference `.spec.md`, `.spec.yaml`, or `.spec.yml` library files
- external references (`external://provider/id`) are deny-by-default and
  require explicit capability + harness policy allowlist
- Canonical in-repo library case surfaces under `specs/libraries` MUST be
  `.spec.md`; yaml/yml include support exists for non-canonical external
  adapter surfaces only.

## Library Document Shape

Library files are normal spec docs containing `type: spec.export` producer cases.

Required fields for each producer case:

- `id`
- `type: spec.export`
- `assert` (list of step mappings whose `checks` carry function bodies)
- `harness.exports` (list of exported symbols)
  - each export entry uses:
    - `as` (symbol name)
    - `from: assert.function`
    - `path` (producer assert step id path)
    - `params` (ordered argument names)

Optional fields:

- `imports` (list[string]): additional library files loaded before this one

Export model:

- Exported symbols are declared explicitly in `harness.exports`.
- Export bodies are compiled from producer assert steps referenced by
  `path` with `from: assert.function`.

## Resolution Rules

- Load order is deterministic and import-first.
- Import cycles MUST fail with schema error.
- Duplicate exported symbol names across loaded libraries MUST fail.
- Symbol resolution for evaluation is:
  - local `let` / function params
  - imported library symbols
  - core builtins

## Determinism and Safety

- Library expressions execute in the same bounded spec-lang evaluator.
- No implementation-defined host callbacks are allowed.
- Errors in library loading/binding are schema failures.
