# Governance Cases

## DCGOV-RUNTIME-PREPUSH-002

```yaml contract-spec
id: DCGOV-RUNTIME-PREPUSH-002
title: makefile contains no python parity prepush targets
purpose: Ensures contributor-facing make targets do not expose python runner lane execution.
type: contract.check
harness:
  root: .
  make_python_parity:
    path: /Makefile
    required_tokens:
    - 'prepush: ## Required local pre-push gate (default rust critical-gate path)'
    - SPEC_PREPUSH_MODE=critical ./scripts/local_ci_parity.sh
    - 'prepush-fast: ## Rust-only critical pre-push mode'
    forbidden_tokens:
    - 'python-parity:'
    - --impl python
    - SPEC_PREPUSH_MODE=parity
  check:
    profile: governance.scan
    config:
      check: runtime.make_python_parity_targets_forbidden
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
