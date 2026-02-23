```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    check:
      profile: governance.scan
      config:
        check: library.domain_index_sync
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
  - id: DCGOV-LIB-INDEX-001
    title: library domain indexes are synchronized
    purpose: Ensures each library domain index lists all library files and exported
      symbols without stale entries.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - library.domain_index_sync
adapters:
- type: beta.scan
  actions:
  - id: act.gov.library.domain.index.syn.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.library.domain.index.syn.1
  consumes:
  - act.gov.library.domain.index.syn.1
```
