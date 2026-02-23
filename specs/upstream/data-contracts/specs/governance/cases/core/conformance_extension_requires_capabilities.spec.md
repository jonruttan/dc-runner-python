```yaml contract-spec
id: DCGOV-CONF-PORT-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: extension type conformance cases declare requires.capabilities
purpose: Ensures non-core type fixtures explicitly declare required capabilities for portable
  parity.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: conformance.extension_requires_capabilities
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
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - conformance.extension_requires_capabilities
    imports:
    - from: artifact
      names:
      - summary_json
```
