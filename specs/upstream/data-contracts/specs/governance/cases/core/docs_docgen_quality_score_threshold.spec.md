# Governance Cases

## DCGOV-DOCS-GEN-026

```yaml contract-spec
id: DCGOV-DOCS-GEN-026
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docgen quality score meets minimum threshold
purpose: Ensures generated runner/harness/stdlib catalogs meet minimum semantic quality score.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.docgen_quality_score_threshold
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
    - summary_json
  steps:
  - id: assert_1
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.docgen_quality_score_threshold
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```
