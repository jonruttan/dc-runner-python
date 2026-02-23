```yaml contract-spec
id: DCGOV-LIVENESS-HARDCAP-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: run trace includes hard-cap and kill escalation reason tokens
purpose: Ensures emergency hard-cap watchdog behavior is represented in trace token taxonomy.
type: contract.check
harness:
  root: .
  liveness_trace_tokens:
    trace_path: specs/governance/cases/fixtures/run_trace_liveness_sample.json
  check:
    profile: governance.scan
    config:
      check: runtime.liveness_hard_cap_token_emitted
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
