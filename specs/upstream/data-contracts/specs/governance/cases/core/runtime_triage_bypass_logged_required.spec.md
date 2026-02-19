# Governance Cases

## DCGOV-RUNTIME-TRIAGE-006

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-006
title: emergency bypass remains explicit and logged
purpose: Ensures pre-push bypass remains explicit and emits deterministic warning output.
type: contract.check
harness:
  root: .
  triage_bypass_logging:
    path: /.githooks/pre-push
    required_tokens:
    - SPEC_PREPUSH_BYPASS
    - 'WARNING: bypass enabled'
  check:
    profile: governance.scan
    config:
      check: runtime.triage_bypass_logged_required
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
