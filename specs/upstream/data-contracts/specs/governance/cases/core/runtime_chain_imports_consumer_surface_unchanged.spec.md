# runtime_chain_imports_consumer_surface_unchanged

```yaml contract-spec
id: DCGOV-HARNESS-EXPORTS-004
title: chain imports consumer surface remains unchanged
purpose: Ensures consumer bindings continue to use harness.chain.imports semantics.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: runtime.chain_imports_consumer_surface_unchanged
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
