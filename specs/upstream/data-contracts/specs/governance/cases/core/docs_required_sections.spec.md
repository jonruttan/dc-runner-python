# Governance Cases

## DCGOV-DOCS-REF-003

```yaml contract-spec
id: DCGOV-DOCS-REF-003
title: key reference chapters include required sections
purpose: Keeps the core reference pages structurally complete by requiring stable section
  tokens for author and implementer workflows.
type: contract.check
harness:
  root: .
  required_sections:
    docs/book/20_case_model.md:
    - '## Canonical Top-Level Topology'
    - '## Responsibility Split'
    - '## Contract Form'
    - '## Normative References'
    docs/book/30_assertion_model.md:
    - '## Canonical Contract Shape'
    - '## Imports and Precedence'
    - '## Forbidden Legacy Forms'
    - '## Group Semantics'
    docs/book/90_reference_guide.md:
    - '## Normative Sources'
    - '## Generated References'
    docs/book/reference_index.md:
    - '# Reference Index'
    - Canonical order for reference-manual chapters.
    - how to use
    docs/book/40_spec_lang_authoring.md:
    - '## Mapping-AST Rules'
    - '## Readability Patterns'
    - '## Anti-Patterns'
    - '## Library-Backed Reuse'
    docs/book/60_runner_and_gates.md:
    - '## Required Rust Lane'
    - '## Gate Sequence'
    - '## Exit Code Semantics'
    - '## Compatibility (Non-Blocking)'
    docs/book/80_troubleshooting.md:
    - '## Failure Taxonomy'
    - '## Deterministic Recovery Flow'
    - '## Escalation'
  check:
    profile: governance.scan
    config:
      check: docs.required_sections
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.required_sections
    imports:
    - from: artifact
      names:
      - summary_json
```
