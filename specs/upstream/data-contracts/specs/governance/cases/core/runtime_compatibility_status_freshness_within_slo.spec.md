# Governance Cases

## DCGOV-RUNTIME-STATUS-004

```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-004
title: compatibility status freshness is bounded by SLO
purpose: Ensures compatibility status telemetry enforces the 72-hour freshness budget.
type: contract.check
harness:
  root: .
  freshness_policy:
    files:
    - /scripts/runner_status_ingest.sh
    - /scripts/ci_gate.sh
    required_tokens:
    - --max-age-hours
    - "72"
    - --enforce-freshness
    - compatibility_stale_or_missing_count
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_status_freshness_within_slo
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

