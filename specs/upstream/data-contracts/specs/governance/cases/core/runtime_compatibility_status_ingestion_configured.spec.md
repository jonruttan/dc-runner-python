# Governance Cases

## DCGOV-RUNTIME-STATUS-003

```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: compatibility status ingestion is configured
purpose: Ensures status exchange ingestion is wired to release assets and matrix artifacts.
type: contract.check
harness:
  root: .
  status_ingestion:
    files:
    - /scripts/runner_status_ingest.sh
    - /specs/schema/runner_certification_registry_v1.yaml
    required_tokens:
    - release_api_url
    - report_asset_name
    - runner-status-matrix.json
    - runner-status-ingest-log.json
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_status_ingestion_configured
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```

