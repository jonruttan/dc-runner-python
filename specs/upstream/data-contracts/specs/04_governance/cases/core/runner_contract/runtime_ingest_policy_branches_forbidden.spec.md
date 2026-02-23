```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PIPE-INGEST-002
    title: ingest policy branch handling
    purpose: Ensures ingest script does not hard-fail on freshness policy branches.
    harness:
      root: "."
      ingest_script:
        path: "/scripts/runner_status_ingest.sh"
        must_not_contain:
        - ERROR: compatibility status freshness policy violation
        - exit 1
      check:
        profile: governance.scan
        config:
          check: runtime.ingest_policy_branches_forbidden
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
```
