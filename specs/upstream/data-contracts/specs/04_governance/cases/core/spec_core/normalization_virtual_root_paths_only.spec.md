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
        check: normalization.virtual_root_paths_only
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
  - id: DCGOV-NORM-PATHS-001
    title: scoped spec paths use canonical virtual-root form
    purpose: Ensures path-bearing spec fields use canonical virtual-root `/...` form.
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
          - normalization.virtual_root_paths_only
adapters:
- type: beta.scan
  actions:
  - id: act.gov.normalization.virtual.ro.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.normalization.virtual.ro.1
  consumes:
  - act.gov.normalization.virtual.ro.1
```
