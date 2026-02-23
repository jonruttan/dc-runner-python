```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    stdlib_conformance:
      required_paths:
      - /specs/03_conformance/cases/core/spec_lang_stdlib.spec.md
      - /specs/03_conformance/cases/core/spec_lang_schema.spec.md
    check:
      profile: governance.scan
      config:
        check: spec_lang.stdlib_conformance_coverage
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
  - id: DCGOV-STDLIB-004
    title: stdlib conformance coverage files are present
    purpose: Ensures canonical stdlib conformance fixtures are present and discoverable.
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
  - id: act.gov.spec.lang.stdlib.conform.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.spec.lang.stdlib.conform.1
  consumes:
  - act.gov.spec.lang.stdlib.conform.1
```
