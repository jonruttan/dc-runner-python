# Conformance Contract (v1)

Implementations are conformant when equivalent fixture sets produce equivalent:

- pass/fail status per case id
- failure category per case id

Stack traces and language-specific exception classes need not match.

## Expected Outcomes DSL

Conformance cases define expected outcomes directly in case records using:

- `expect.portable`: shared expectations for all implementations
- `expect.impl.<name>`: implementation-specific overrides (for example
  `python`, `php`)

Expected keys:

- `status`: `pass`, `fail`, or `skip`
- `category`: `schema` / `assertion` / `runtime` / `null`
- `message_tokens`: optional list of tokens expected in failure messages

Resolution order:

1. Start from `expect.portable`.
2. If `expect.impl.<implementation>` exists, overlay its keys.

`expect` is required for conformance fixture cases.

## Capability Requirements

Cases may declare capability requirements under `requires`:

- `capabilities`: list of required capability strings
- `when_missing`: `skip` or `fail` (default `fail`)
- capability names are implementation-defined strings (for example `cli.run`)

Execution behavior:

- if all required capabilities are present: evaluate the case normally
- if required capabilities are missing and `when_missing=skip`: result is `skip`
- if required capabilities are missing and `when_missing=fail`: result is `fail`
  with category `runtime`

## Capability Parity Scope

Parity comparison across implementations MUST be evaluated on the intersection
of:

- shared expected-outcome ids (`expect` overlay resolved per implementation), and
- shared capability ids (cases whose `requires.capabilities` are satisfied by
  both implementations).

For extension/domain types, parity mismatches are actionable only when both
implementations declare and satisfy the same required capabilities for that
case.

## Test Authoring Policy

- Behavior tests SHOULD be represented as executable `.spec.md` fixtures.
- Direct unit tests (`tests/test_*_unit.py`) are disallowed by default.
- A direct unit test MAY be used only when the behavior cannot be expressed
  safely or clearly in the `yaml contract-spec` DSL/harness contract.
- Any unit test file MUST declare an explicit opt-out reason at the top of the
  file using:
  - `# SPEC-OPT-OUT: <specific reason>`
