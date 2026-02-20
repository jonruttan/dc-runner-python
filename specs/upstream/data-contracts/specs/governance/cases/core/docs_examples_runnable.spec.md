# Governance Cases

## DCGOV-DOCS-REF-004

```yaml contract-spec
id: DCGOV-DOCS-REF-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: reference examples parse or are explicitly opted out
purpose: Ensures reference examples are trustworthy by requiring parseable or statically valid
  fenced examples unless explicitly opted out.
type: contract.check
harness:
  root: .
  docs_examples:
    files:
    - docs/book/10_getting_started.md
    - docs/book/20_case_model.md
    - docs/book/30_assertion_model.md
    - docs/book/40_spec_lang_authoring.md
    - docs/book/60_runner_and_gates.md
    - docs/book/80_troubleshooting.md
    - docs/book/90_reference_guide.md
    - docs/development.md
  check:
    profile: governance.scan
    config:
      check: docs.examples_runnable
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
      - docs.examples_runnable
    imports:
    - from: artifact
      names:
      - summary_json
```
