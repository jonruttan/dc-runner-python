```yaml contract-spec
id: DCGOV-RUNTIME-SHELL-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: shell policy branches forbidden in control-plane dispatcher
purpose: Ensures active control-plane shell entrypoints do not embed policy verdict branching text.
type: contract.check
harness:
  root: .
  control_plane_shell:
    path: /scripts/control_plane.sh
    forbidden_tokens:
      - README missing required task path token
      - runtime runner execution references are forbidden
      - missing required file:
  check:
    profile: governance.scan
    config:
      check: runtime.shell_policy_branches_forbidden
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
