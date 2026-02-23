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
        check: docs.governance_check_family_map_complete
contracts:
  clauses:
  - id: DCGOV-DOCS-CANON-002
    title: governance check family map covers all registered checks
    purpose: Ensures each governance check id is mapped to a canonical check family
      prefix.
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
  - id: act.gov.docs.governance.check.fa.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.governance.check.fa.1
  consumes:
  - act.gov.docs.governance.check.fa.1
```
