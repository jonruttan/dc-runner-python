```yaml contract-spec
id: DCGOV-PROFILE-REDACT-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: run trace redaction policy prevents secret leakage
purpose: Ensures profiling env metadata does not store raw values and trace payloads do not
  include common secret-like tokens.
type: contract.check
harness:
  root: .
  profiling_redaction:
    trace_path: specs/governance/cases/fixtures/run_trace_sample.json
  check:
    profile: governance.scan
    config:
      check: runtime.profiling_redaction_policy
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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

