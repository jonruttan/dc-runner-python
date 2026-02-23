```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    examples_prefer_domain_fs_helpers:
      files:
      - docs/book/60_runner_and_gates.md
      - docs/book/90_reference_guide.md
      - specs/02_contracts/04_harness.md
    check:
      profile: governance.scan
      config:
        check: docs.examples_prefer_domain_fs_helpers
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
  - id: DCGOV-DOCS-FS-EXAMPLES-001
    title: docs yaml examples prefer domain fs/path helpers over raw ops fs
    purpose: Keeps contributor-facing docs examples aligned with the domain-library-first
      authoring model for filesystem/json/glob/path flows.
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
  - id: act.gov.docs.examples.prefer.dom.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.examples.prefer.dom.1
  consumes:
  - act.gov.docs.examples.prefer.dom.1
```
