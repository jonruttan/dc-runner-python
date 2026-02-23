```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    compatibility_matrix:
      path: /specs/02_contracts/25_compatibility_matrix.md
      required_tokens:
      - '- `required`:'
      - '- `compatibility_non_blocking`:'
      - '- `rust`'
      - '- `python`'
      - '- `php`'
      - '- `node`'
      - '- `c`'
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_matrix_registration_required
    use:
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CONFIG-008
    title: compatibility matrix registration is explicit
    purpose: Ensures runtime lanes are registered in the compatibility matrix contract
      before use.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.compatibility.ma.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.compatibility.ma.1
  consumes:
  - act.gov.runtime.compatibility.ma.1
```
