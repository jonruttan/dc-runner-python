```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    compatibility_docs:
      files:
      - /README.md
      - /docs/development.md
      - /specs/02_contracts/12_runner_interface.md
      required_tokens:
      - implementation-agnostic
      - compatibility lanes
      - non-blocking
      forbidden_tokens:
      - ./scripts/ci_gate.sh
    check:
      profile: governance.scan
      config:
        check: docs.compatibility_examples_labeled
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
  - id: DCGOV-DOCS-REF-008
    title: compatibility examples are explicitly labeled
    purpose: Ensures active documentation keeps Rust as canonical and labels Python/PHP
      examples as non-blocking compatibility lanes.
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
  - id: act.gov.docs.compatibility.examp.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.compatibility.examp.1
  consumes:
  - act.gov.docs.compatibility.examp.1
```
