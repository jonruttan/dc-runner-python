```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: runner status report schema is defined
purpose: Ensures runner status exchange producer payload shape is declared and stable.
type: contract.check
harness:
  root: .
  runner_status_report_schema:
    path: /specs/01_schema/runner_status_report_v1.yaml
    required_tokens:
    - type: runtime.runner_status_report
    - runner_id
    - implementation_repo
    - generated_at
    - fresh_until
    - command_results
    - artifact_refs
  check:
    profile: governance.scan
    config:
      check: runtime.runner_status_report_schema_valid
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

