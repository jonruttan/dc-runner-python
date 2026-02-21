```yaml contract-spec
id: DCGOV-ARCH-COMPONENTS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: harnesses must use shared workflow components
purpose: Enforces hard-cut architecture by requiring shared execution context, assertion engine,
  and subject router wiring in all harnesses.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: architecture.harness_workflow_components_required
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

