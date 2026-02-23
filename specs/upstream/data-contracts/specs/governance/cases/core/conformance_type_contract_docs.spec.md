```yaml contract-spec
id: DCGOV-CONF-TYPE-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: conformance case types have matching type contract docs
purpose: Ensures each type used by portable conformance fixtures is documented under the type-contract
  index.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: conformance.type_contract_docs
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
      - conformance.type_contract_docs
    imports:
    - from: artifact
      names:
      - summary_json
```
