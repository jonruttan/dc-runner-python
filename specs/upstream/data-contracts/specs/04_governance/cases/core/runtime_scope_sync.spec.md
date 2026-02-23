```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    runtime_scope:
      files:
      - specs/02_contracts/08_v1_scope.md
      - specs/02_contracts/13_runtime_scope.md
      - specs/02_contracts/12_runner_interface.md
      required_tokens:
      - Python runner
      - PHP runner
      - required support targets
      - contract/governance expansion
      forbidden_tokens:
      - Node.js runner
      - Ruby runner
      - Java runner
    check:
      profile: governance.scan
      config:
        check: runtime.scope_sync
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
  - id: DCGOV-RUNTIME-SCOPE-001
    title: runtime support scope remains bounded for v1
    purpose: Prevents uncontrolled cross-runtime expansion by enforcing explicit v1
      runtime scope tokens in contract docs.
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
      - id: assert_2
        assert:
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - runtime.scope_sync
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.scope.sync.spec.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.scope.sync.spec.1
  consumes:
  - act.gov.runtime.scope.sync.spec.1
```
