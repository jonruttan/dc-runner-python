```yaml contract-spec
id: DCGOV-DOCS-QUAL-009
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: release contract forbids manual sequential checklist choreography
purpose: Ensures release guidance uses executable gate entrypoints and codifies that manual
  do-X-then-inspect-Y sequences are an anti-pattern.
type: contract.check
harness:
  root: .
  release_contract:
    files:
    - docs/release_checklist.md
    required_tokens:
    - Release readiness is defined by executable gates, not manual checklists.
    - make ci-smoke
    - ./scripts/ci_gate.sh
    - convert it into an executable
    forbidden_patterns:
    - (?m)^##\s+[0-9]+\)
    - (?m)^\s*[0-9]+\.\s+(Run|Then|Check|Inspect)\b
  check:
    profile: governance.scan
    config:
      check: docs.release_contract_automation_policy
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
      - docs.release_contract_automation_policy
    imports:
    - from: artifact
      names:
      - summary_json
```
