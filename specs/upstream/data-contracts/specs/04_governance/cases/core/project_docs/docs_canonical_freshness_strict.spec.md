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
        check: docs.canonical_freshness_strict
contracts:
  clauses:
  - id: DCGOV-DOCS-CANON-003
    title: docs freshness strict checker passes
    purpose: Ensures specs freshness checks are strict, deterministic, and currently
      clean.
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
  - id: act.gov.docs.canonical.freshness.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.canonical.freshness.1
  consumes:
  - act.gov.docs.canonical.freshness.1
```
