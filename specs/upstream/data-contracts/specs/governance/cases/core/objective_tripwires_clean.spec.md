```yaml contract-spec
id: DCGOV-OBJECTIVE-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: objective tripwires are clean
purpose: Ensures objective manifest tripwire checks map to valid governance checks and currently
  pass.
type: contract.check
harness:
  root: .
  objective_tripwires:
    manifest_path: /specs/governance/metrics/objective_manifest.yaml
    cases_path: /specs/governance/cases
    case_file_pattern: '*.spec.md'
  check:
    profile: governance.scan
    config:
      check: objective.tripwires_clean
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
      - objective.tripwires_clean
    imports:
    - from: artifact
      names:
      - summary_json
```
