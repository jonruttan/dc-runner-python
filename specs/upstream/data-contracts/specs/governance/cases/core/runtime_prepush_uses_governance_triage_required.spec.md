# Governance Cases

## DCGOV-RUNTIME-TRIAGE-002

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-002
title: prepush lane uses governance triage entrypoint
purpose: Ensures prepush parity lane calls governance triage instead of direct broad governance.
type: contract.check
harness:
  root: .
  prepush_governance_triage:
    path: /scripts/local_ci_parity.sh
    required_tokens:
    - governance-triage
    - ./scripts/governance_triage.sh --mode broad-first --impl
    forbidden_tokens:
    - run_step governance "${SPEC_RUNNER_BIN}" --impl "${SPEC_RUNNER_IMPL}" governance
  check:
    profile: governance.scan
    config:
      check: runtime.prepush_uses_governance_triage_required
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
