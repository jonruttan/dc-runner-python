```yaml contract-spec
id: DCGOV-STUB-CONFORMANCE_SPEC_LANG_PREFERRED
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: stub case for conformance_spec_lang_preferred
purpose: Maintains traceability reference integrity for conformance_spec_lang_preferred.
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
