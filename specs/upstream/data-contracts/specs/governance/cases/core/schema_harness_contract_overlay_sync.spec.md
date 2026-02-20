# Governance Cases

## DCGOV-ARCH-COMPONENTS-004

```yaml contract-spec
id: DCGOV-ARCH-COMPONENTS-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: harness contract and overlays remain synchronized
purpose: Verifies contract/current docs and harness type overlays describe the same orchestration.run
  and docs.generate architecture.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: schema.harness_contract_overlay_sync
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

