```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-RCERT-001
    title: runner execution certificate v1 schema is declared
    purpose: Ensures the v1 runner execution certificate schema is present with core
      sections.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - type
          - runtime.runner_execution_certificate
        - call:
          - var: policy.text.contains_pair
          - var: text
          - version
          - '2'
  - id: DCCONF-RCERT-002
    title: runner execution certificate v1 includes intent equivalence and proof
    purpose: Ensures v1 schema defines deterministic intent and payload proof fields.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - execution_intent
          - registry_ref
        - call:
          - var: policy.text.contains_pair
          - var: text
          - equivalence
          - intent_hash
        - call:
          - var: policy.text.contains_pair
          - var: text
          - proof
          - payload_sha256
adapters:
- type: io.fs
  actions:
  - id: svc.assert_check.text_file.1
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_pair
        artifact_id: art.svc.assert_check.text_file.1.use_1.1
    direction: input
    profile: read.text
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
assets:
- id: art.svc.assert_check.text_file.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
```

