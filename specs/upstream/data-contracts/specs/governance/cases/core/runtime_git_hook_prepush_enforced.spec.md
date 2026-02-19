# Governance Cases

## DCGOV-RUNTIME-PREPUSH-003

```yaml contract-spec
id: DCGOV-RUNTIME-PREPUSH-003
title: managed pre-push hook enforces local parity gate
purpose: Ensures repository-managed pre-push hook exists and is installable via canonical
  script.
type: contract.check
harness:
  root: .
  git_hook_prepush:
    hook_path: /.githooks/pre-push
    install_script: /scripts/install_git_hooks.sh
    makefile_path: /Makefile
  check:
    profile: governance.scan
    config:
      check: runtime.git_hook_prepush_enforced
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
