# Contract Rule Template

Use this template when adding or revising a portable contract rule.

## Rule Metadata

- Rule ID: `RULE-ID`
- Introduced In: `vN` (required)
- Retired In: `vN` (optional)
- Removed In: `vN` (optional)
- Norm: `MUST | SHOULD | MUST_NOT`
- Scope: `case | implementation | conformance | runner`
- Applies To: `path/to/subject`

## Requirement

State the requirement in one sentence.

## Rationale

Explain why this rule exists.

## Risk If Violated

Describe likely failure modes or operational risk.

## Non-Goals

State what this rule intentionally does not require.

## Examples

- Positive example(s)
- Negative/counter example(s)

## Evidence Mapping

- Policy entry: `specs/02_contracts/policy_v1.yaml`
- Traceability entry: `specs/02_contracts/traceability_v1.yaml`
- Conformance case id(s): `...`
- Unit/integration tests: `...`
- Implementation paths: `...`
