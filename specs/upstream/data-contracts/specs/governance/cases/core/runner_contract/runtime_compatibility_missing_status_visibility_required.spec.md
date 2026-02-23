```yaml contract-spec
id: DCGOV-RUNTIME-STATUS-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: missing compatibility status remains visible
purpose: Ensures missing compatibility status is visible and policy-scored in matrix output.
type: contract.check
harness:
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

