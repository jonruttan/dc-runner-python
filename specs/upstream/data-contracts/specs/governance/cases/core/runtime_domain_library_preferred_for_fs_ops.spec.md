```yaml contract-spec
id: DCGOV-DOMAIN-LIB-OPS-FS-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: executable specs prefer domain library helpers over raw ops fs symbols
purpose: Enforces domain.path/domain.fs usage in executable specs and allows raw ops.fs usage
  only in stdlib primitive conformance coverage.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.domain_library_preferred_for_fs_ops
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
    - summary_json
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
