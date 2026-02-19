# Governance Cases

## DCGOV-RUNTIME-META-TARGET-001

```yaml contract-spec
id: DCGOV-RUNTIME-META-TARGET-001
title: executable harnesses expose meta_json assertion target
purpose: Ensures all core executable harness adapters project meta_json.
type: contract.check
harness:
  root: .
  meta_json_targets:
    files:
    - /dc-runner-python
    - /dc-runner-python
    - /dc-runner-python
    - /dc-runner-python
    - /dc-runner-python
    required_tokens:
    - meta_json
  check:
    profile: governance.scan
    config:
      check: runtime.meta_json_target_required
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
```
