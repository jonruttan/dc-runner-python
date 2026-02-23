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
        check: runtime.harness_exports_location_required
contracts:
  clauses:
  - id: DCGOV-HARNESS-EXPORTS-001
    title: producer exports are declared at harness.exports
    purpose: Ensures producer symbol declarations are declared at harness.exports
      and canonical harness.chain.exports is rejected.
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
  - id: act.gov.runtime.harness.exports.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.harness.exports.1
  consumes:
  - act.gov.runtime.harness.exports.1
```
