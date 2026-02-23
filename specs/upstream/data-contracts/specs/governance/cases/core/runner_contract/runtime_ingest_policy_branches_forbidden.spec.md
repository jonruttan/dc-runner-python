```yaml contract-spec
id: DCGOV-PIPE-INGEST-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: ingest policy branch exits are forbidden
purpose: Ensures ingest script does not hard-fail on freshness policy branches.
type: contract.check
harness:
  root: .
  ingest_script:
    path: /scripts/runner_status_ingest.sh
    must_not_contain:
      - ERROR: compatibility status freshness policy violation
      - exit 1
  check:
    profile: governance.scan
    config:
      check: runtime.ingest_policy_branches_forbidden
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
