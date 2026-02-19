# Governance Cases

## DCGOV-RUNTIME-CONTRACT-SPEC-001

```yaml contract-spec
id: DCGOV-RUNTIME-CONTRACT-SPEC-001
title: executable case fences must use contract-spec
purpose: Enforces hard-cut fence rename to contract-spec across specs cases.
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
      check: runtime.contract_spec_fence_required
```
