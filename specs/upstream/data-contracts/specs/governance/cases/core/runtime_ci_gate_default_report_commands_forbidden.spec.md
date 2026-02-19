# Governance Cases

## DCGOV-RUNTIME-TRIAGE-016

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-016
title: default ci gate excludes report-generation commands
purpose: Ensures ci-gate-summary default step list does not include report-generation command
  invocations.
type: contract.check
harness:
  root: .
  ci_gate_default_reports_forbidden:
    files:
    - /dc-runner-python
    - /dc-runner-rust
    forbidden_tokens:
    - spec_portability_json
    - spec_portability_md
    - spec_lang_adoption_json
    - spec_lang_adoption_md
    - runner_independence_json
    - runner_independence_md
    - python_dependency_json
    - python_dependency_md
    - docs_operability_json
    - docs_operability_md
    - contract_assertions_json
    - contract_assertions_md
    - objective_scorecard_json
    - objective_scorecard_md
    - spec_lang_stdlib_json
    - spec_lang_stdlib_md
    - conformance_purpose_json
    - conformance_purpose_md
  check:
    profile: governance.scan
    config:
      check: runtime.ci_gate_default_report_commands_forbidden
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
```
