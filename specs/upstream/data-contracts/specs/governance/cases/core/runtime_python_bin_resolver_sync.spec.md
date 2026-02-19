# Governance Cases

## DCGOV-RUNTIME-CONFIG-002

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-002
title: python-invoking adapter scripts use shared python-bin resolver helper
purpose: Keeps shared Python resolver helper contract stable for remaining tooling paths.
type: contract.check
harness:
  root: .
  python_bin_resolver:
    helper: scripts/lib/python_bin.sh
    files:
    - scripts/lib/python_bin.sh
    required_tokens:
    - resolve_python_bin() {
    - ${root_dir}/.venv/bin/python
    - ${root_dir}/../../.venv/bin/python
    - python3
    forbidden_tokens: []
  check:
    profile: governance.scan
    config:
      check: runtime.compatibility_python_lane_bin_resolver_sync
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
      - runtime.compatibility_python_lane_bin_resolver_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
