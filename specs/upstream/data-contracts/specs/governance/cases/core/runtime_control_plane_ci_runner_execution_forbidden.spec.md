# Governance Cases

## DCGOV-RUNTIME-CI-001

```yaml contract-spec
id: DCGOV-RUNTIME-CI-001
title: control-plane ci forbids runtime runner execution
purpose: Ensures this repository CI does not execute runtime lanes directly.
type: contract.check
harness:
  root: .
  ci_runtime_exec:
    files:
    - /.github/workflows/ci.yml
    - /scripts/ci_gate.sh
    - /scripts/core_gate.sh
    - /scripts/local_ci_parity.sh
    forbidden_tokens:
    - scripts/runner_bin.sh
  check:
    profile: governance.scan
    config:
      check: runtime.control_plane_ci_runner_execution_forbidden
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
