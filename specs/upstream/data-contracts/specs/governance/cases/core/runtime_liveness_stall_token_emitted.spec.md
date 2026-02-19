# Governance Cases

## DCGOV-LIVENESS-STALL-001

```yaml contract-spec
id: DCGOV-LIVENESS-STALL-001
title: run trace contains liveness stall reason tokens
purpose: Ensures watchdog reason tokens for runner/subprocess stall semantics are observable
  in run trace artifacts.
type: contract.check
harness:
  root: .
  liveness_trace_tokens:
    trace_path: specs/governance/cases/fixtures/run_trace_liveness_sample.json
    required_tokens:
    - stall.runner.no_progress
    - stall.subprocess.no_output_no_event
  check:
    profile: governance.scan
    config:
      check: runtime.liveness_stall_token_emitted
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
