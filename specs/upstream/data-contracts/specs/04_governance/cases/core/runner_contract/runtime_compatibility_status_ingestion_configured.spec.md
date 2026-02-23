```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    status_ingestion:
      files:
      - /scripts/runner_status_ingest.sh
      - /specs/01_schema/runner_certification_registry_v1.yaml
      required_tokens:
      - release_api_url
      - report_asset_name
      - runner-status-matrix.json
      - runner-status-ingest-log.json
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_status_ingestion_configured
contracts:
  clauses:
  - id: DCGOV-RUNTIME-STATUS-003
    title: compatibility status ingestion is configured
    purpose: Ensures status exchange ingestion is wired to release assets and matrix
      artifacts.
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

