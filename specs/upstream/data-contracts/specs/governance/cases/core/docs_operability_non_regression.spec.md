# Governance Cases

## DCGOV-DOCS-OPER-002

```yaml contract-spec
id: DCGOV-DOCS-OPER-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docs operability metric is non-regressing
purpose: Enforces monotonic non-regression for docs operability metrics against checked-in
  baseline.
type: contract.check
harness:
  root: .
  docs_operability_non_regression:
    baseline_path: /specs/governance/metrics/docs_operability_baseline.json
    summary_fields:
      overall_docs_operability_ratio: non_decrease
    segment_fields:
      book:
        mean_runnable_example_coverage_ratio: non_decrease
      contract:
        mean_token_sync_compliance_ratio: non_decrease
    epsilon: 1.0e-12
    docs_operability:
      reference_manifest: /docs/book/reference_manifest.yaml
  check:
    profile: governance.scan
    config:
      check: docs.operability_non_regression
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
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
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.operability_non_regression
    imports:
    - from: artifact
      names:
      - summary_json
```
