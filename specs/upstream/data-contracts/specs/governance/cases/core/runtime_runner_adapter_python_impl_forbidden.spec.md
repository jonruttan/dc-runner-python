# Governance Cases

## DCGOV-RUNTIME-ENTRY-003

```yaml contract-spec
id: DCGOV-RUNTIME-ENTRY-003
title: runner adapter hard-fails python impl selection
purpose: Ensures `scripts/runner_bin.sh` rejects `--impl python` with migration
  guidance.
type: contract.check
harness:
  root: .
  runner_adapter_python_impl:
    path: /scripts/runner_bin.sh
    required_tokens:
    - python runner impl is no longer supported on the runtime path
    - Use rust impl instead
    forbidden_tokens:
    - exec "${ROOT_DIR}/dc-runner-python" "$@"
  check:
    profile: governance.scan
    config:
      check: runtime.runner_adapter_python_impl_forbidden
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
```
