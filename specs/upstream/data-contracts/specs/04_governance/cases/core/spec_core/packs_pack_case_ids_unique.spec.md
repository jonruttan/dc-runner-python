```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-006
    title: pack case ids remain unique
    purpose: Ensures newly introduced runner-cli cases do not collide on case id.
    harness:
      root: "."
      runner_cli_cases:
        path: "/specs/03_conformance/cases/runner_cli"
        required_ids:
        - DCCONF-RCLI-001
        - DCCONF-RCLI-002
        - DCCONF-RCLI-003
        - DCCONF-RCLI-004
        - DCCONF-RCLI-005
      check:
        profile: governance.scan
        config:
          check: packs.pack_case_ids_unique
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
