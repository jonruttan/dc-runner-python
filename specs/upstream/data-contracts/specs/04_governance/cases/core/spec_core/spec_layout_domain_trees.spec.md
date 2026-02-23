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
        check: spec.layout_domain_trees
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
  - id: DCGOV-SPECLAYOUT-DOMAIN-001
    title: spec layout uses domain tree directories
    purpose: Ensures conformance, governance, and library specs are organized under
      domain subdirectories with index files.
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
          - spec.layout_domain_trees
adapters:
- type: beta.scan
  actions:
  - id: act.gov.spec.layout.domain.trees.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.spec.layout.domain.trees.1
  consumes:
  - act.gov.spec.layout.domain.trees.1
```
