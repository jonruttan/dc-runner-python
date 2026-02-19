# Governance Cases

## DCGOV-RUNTIME-OPS-OS-SURFACE-001

```yaml contract-spec
id: DCGOV-RUNTIME-OPS-OS-SURFACE-001
title: ops.os stdlib symbols are declared in profile and symbol maps
purpose: Ensures ops.os builtins are synchronized across stdlib mapping and stdlib profile
  contract surfaces.
type: contract.check
harness:
  root: .
  ops_os_stdlib_surface:
    files:
    - /dc-runner-python
    - /specs/schema/spec_lang_stdlib_profile_v1.yaml
    required_symbols:
    - ops.os.exec
    - ops.os.exec_capture
    - ops.os.env_get
    - ops.os.env_has
    - ops.os.cwd
    - ops.os.pid
    - ops.os.sleep_ms
    - ops.os.exit_code
  check:
    profile: governance.scan
    config:
      check: runtime.ops_os_stdlib_surface_sync
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
