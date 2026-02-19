# Governance Cases

## DCGOV-RUNTIME-HOOKS-002

```yaml contract-spec
id: DCGOV-RUNTIME-HOOKS-002
title: when class hook ordering contract required
purpose: Ensures class hooks run only after successful clause pass and before complete.
type: contract.check
harness:
  root: .
  when_ordering:
    path: /dc-runner-python
    required_tokens:
    - def _on_clause_pass
    - 'event_map = {"MUST": "must", "MAY": "may", "MUST_NOT": "must_not"}'
    - event = event_map.get(cls)
    - _run_event(
    - def _on_complete
    - '"complete"'
  check:
    profile: governance.scan
    config:
      check: runtime.when_ordering_contract_required
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
