```yaml contract-spec
id: DCGOV-CHAIN-FORM-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: chain exports use list-only canonical form
purpose: Ensures harness.chain step exports reject non-canonical mapping form and require
  list-form entries.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_exports_list_only_required
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
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
```

