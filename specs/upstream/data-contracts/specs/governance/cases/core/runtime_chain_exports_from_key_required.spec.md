# runtime.chain_exports_from_key_required

```yaml contract-spec
id: DCGOV-CHAIN-FROM-001
title: chain exports use canonical from key
purpose: Ensures harness.chain step exports declare the required from field and do not rely
  on non-canonical key forms.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_exports_from_key_required
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
