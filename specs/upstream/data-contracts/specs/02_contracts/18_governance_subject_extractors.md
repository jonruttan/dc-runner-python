# Governance Subject Extractor Contract (v1)

## Purpose

Defines the extractor/policy split for governance checks:

1. extractor stage gathers deterministic repository data
2. policy stage evaluates `evaluate` via spec-lang

## Extractor Output Shape

Governance check implementations SHOULD return a structured payload with:

- `subject`: primary policy input (rows/report/object)
- `violations`: candidate violation messages (data-only)
- `symbols` (optional): symbol table values for policy evaluation
- `evaluate`: operator-keyed mapping-AST spec-lang expression list
- `policy_path`: source location token for diagnostics
- `summary` (runtime assertion surface):
  - `passed` (bool)
  - `check_id` (string)
  - `case_id` (string)
  - `violation_count` (int)

## Determinism Requirements

- Extractors MUST be deterministic for the same repository state.
- Extractors MUST NOT use ambient time/random/network data.
- Extractors MUST NOT decide final pass/fail directly.

## Policy Requirements

- Final verdict MUST be the result of `evaluate`.
- Governance checks MUST wire shared policy libraries via
  `harness.spec_lang.includes`.
- Governance `evaluate` MUST call exported library symbols.
- Path-bearing governance harness fields use virtual-root canonical `/...`
  semantics (`/` = contract root).
- External refs (`external://provider/id`) are deny-by-default and require
  explicit capability + provider allow policy.
- On policy failure, diagnostics MUST include `case_id`, `check_id`, and
  `policy_path`.
- Check-specific branch text like `"<check> evaluate returned false"`
  MUST NOT be embedded in check implementations.
- Governance assertion contracts SHOULD prefer structured targets
  (`violation_count`, `summary_json` + `evaluate`) instead of PASS text
  markers as primary truth.

## Migration Notes

For scanner-first checks:

- keep scanner logic as extractor data production
- move boolean gate logic into `evaluate`
- preserve stable violation messages for CI diagnostics
