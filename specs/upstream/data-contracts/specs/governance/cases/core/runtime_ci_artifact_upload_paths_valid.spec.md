# Governance Cases

## DCGOV-RUNTIME-TRIAGE-013

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-013
title: ci workflow uploads artifacts from canonical .artifacts path
purpose: Ensures CI uploads gate and triage artifacts using a recursive .artifacts path.
type: contract.check
harness:
  root: .
  ci_artifact_upload:
    path: /.github/workflows/ci.yml
    required_tokens:
    - actions/upload-artifact@v4
    - .artifacts/**
    - 'if: always()'
  check:
    profile: governance.scan
    config:
      check: runtime.ci_artifact_upload_paths_valid
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
