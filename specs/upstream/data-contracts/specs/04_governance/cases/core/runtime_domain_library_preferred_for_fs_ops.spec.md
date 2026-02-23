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
        check: runtime.domain_library_preferred_for_fs_ops
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
  - id: DCGOV-DOMAIN-LIB-OPS-FS-001
    title: executable specs prefer domain library helpers over raw ops fs symbols
    purpose: Enforces domain.path/domain.fs usage in executable specs and allows raw
      ops.fs usage only in stdlib primitive conformance coverage.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.domain.library.p.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.domain.library.p.1
  consumes:
  - act.gov.runtime.domain.library.p.1
```
