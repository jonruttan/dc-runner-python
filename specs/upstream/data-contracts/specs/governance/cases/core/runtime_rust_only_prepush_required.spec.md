```yaml contract-spec
id: DCGOV-RUNTIME-PREPUSH-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: prepush path is rust-only
purpose: Ensures prepush entrypoints and hook routing remain rust-only.
type: contract.check
harness:
  root: .
  rust_only_prepush:
    file_token_sets:
    - path: /scripts/ci_gate.sh
      required_tokens:
      - 'mode=critical: rust-only critical path'
      forbidden_tokens:
      - lane_python_parity
      - --impl python
      - expected critical|parity|fast
    - path: /.githooks/pre-push
      required_tokens:
      - make prepush
      forbidden_tokens:
      - --impl python
      - SPEC_PREPUSH_MODE=parity
    - path: /Makefile
      required_tokens:
      - SPEC_PREPUSH_MODE=critical ./scripts/ci_gate.sh
      forbidden_tokens:
      - 'python-parity:'
      - SPEC_PREPUSH_MODE=parity ./scripts/ci_gate.sh
  check:
    profile: governance.scan
    config:
      check: runtime.required_lane_only_prepush_required
  use:
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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
