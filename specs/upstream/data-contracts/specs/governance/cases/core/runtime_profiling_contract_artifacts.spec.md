# Governance Cases

## DCGOV-PROFILE-CONTRACT-001

```yaml contract-spec
id: DCGOV-PROFILE-CONTRACT-001
title: runtime profiling contract artifacts exist and are discoverable
purpose: Ensures run trace schema and profiling contract docs are present and linked in current
  snapshot notes.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.profiling_contract_artifacts
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

