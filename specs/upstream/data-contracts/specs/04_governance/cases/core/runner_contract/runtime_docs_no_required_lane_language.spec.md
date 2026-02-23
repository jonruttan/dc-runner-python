```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_language:
      files:
      - /README.md
      - /docs/development.md
      - /docs/book/index.md
      - /docs/book/60_runner_and_gates.md
      required_tokens:
      - implementation-agnostic control plane
      - runtime execution ownership lives in runner repositories
    check:
      profile: governance.scan
      config:
        check: runtime.docs_no_required_lane_language
contracts:
  clauses:
  - id: DCGOV-RUNTIME-DOCS-001
    title: docs use control-plane language
    purpose: Ensures active docs describe this repository as implementation-agnostic
      control-plane.
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
  - id: act.gov.runtime.docs.no.required.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.docs.no.required.1
  consumes:
  - act.gov.runtime.docs.no.required.1
```
