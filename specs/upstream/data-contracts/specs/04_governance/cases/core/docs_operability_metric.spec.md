```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-STUB-DOCS_OPERABILITY_METRIC
    title: stub case for docs_operability_metric
    purpose: Maintains traceability reference integrity for docs_operability_metric.
    harness:
      root: "."
      check:
        profile: governance.scan
        config:
          check: governance.structured_assertions_required
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
