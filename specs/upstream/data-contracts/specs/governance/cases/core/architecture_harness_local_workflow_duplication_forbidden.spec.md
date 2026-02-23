```yaml contract-spec
id: DCGOV-ARCH-COMPONENTS-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: non-canonical harness workflow duplication is forbidden
purpose: Prevents harness modules from reintroducing local spec-lang setup and direct assertion-evaluation
  glue after component hard cut.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: architecture.harness_local_workflow_duplication_forbidden
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

