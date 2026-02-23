```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    status_visibility:
      path: /scripts/runner_status_ingest.sh
      required_tokens:
      - freshness_state
      - missing
      - policy_effect
      - non_blocking_fail
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_missing_status_visibility_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-005
    title: missing compatibility status remains visible
    purpose: Ensures missing compatibility status is visible and policy-scored in
      matrix output.
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
  - id: act.gov.runtime.compatibility.mi.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.compatibility.mi.1
  consumes:
  - act.gov.runtime.compatibility.mi.1
```

