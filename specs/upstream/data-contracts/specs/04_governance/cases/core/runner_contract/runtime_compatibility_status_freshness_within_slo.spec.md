```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    freshness_policy:
      files:
      - /scripts/runner_status_ingest.sh
      - /scripts/ci_gate.sh
      required_tokens:
      - --max-age-hours
      - '72'
      - --enforce-freshness
      - compatibility_stale_or_missing_count
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_status_freshness_within_slo
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-004
    title: compatibility status freshness is bounded by SLO
    purpose: Ensures compatibility status telemetry enforces the 72-hour freshness
      budget.
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
  - id: act.gov.runtime.compatibility.st.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.compatibility.st.1
  consumes:
  - act.gov.runtime.compatibility.st.1
```

