```yaml contract-spec
id: DCGOV-STUB-SPEC_LANG_ADOPTION_METRIC
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: stub case for spec_lang_adoption_metric
purpose: Maintains traceability reference integrity for spec_lang_adoption_metric.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: governance.structured_assertions_required
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
