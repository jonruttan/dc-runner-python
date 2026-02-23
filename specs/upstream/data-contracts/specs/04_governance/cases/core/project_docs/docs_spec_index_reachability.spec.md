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
        check: docs.spec_index_reachability
contracts:
  clauses:
  - id: DCGOV-DOCS-CANON-001
    title: specs index links all canonical spec entrypoints
    purpose: Ensures /specs/index.md links every canonical spec subtree and current
      snapshot.
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
  - id: act.gov.docs.spec.index.reachabi.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.spec.index.reachabi.1
  consumes:
  - act.gov.docs.spec.index.reachabi.1
```
