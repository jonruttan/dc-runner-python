# Governance Cases

## DCGOV-RUNTIME-CONTRACT-STEP-001

```yaml contract-spec
id: DCGOV-RUNTIME-CONTRACT-STEP-001
title: contract steps must declare asserts
purpose: Enforces step-form contract nodes to use asserts list and non-empty children.
type: contract.check
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
harness:
  check:
    profile: governance.scan
    config:
      check: runtime.contract_step_asserts_required
```
