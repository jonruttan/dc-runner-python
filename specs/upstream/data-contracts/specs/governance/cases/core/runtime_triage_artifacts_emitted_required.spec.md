# Governance Cases

## DCGOV-RUNTIME-TRIAGE-004

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-004
title: triage artifacts are emitted by triage and gate flows
purpose: Ensures triage artifacts are produced and referenced by governance-triage and ci-gate-summary.
type: contract.check
harness:
  root: .
  triage_artifacts:
    files:
    - /scripts/governance_triage.sh
    - /dc-runner-python
    required_tokens:
    - failing_check_ids
    - failing_check_prefixes
  check:
    profile: governance.scan
    config:
      check: runtime.triage_artifacts_emitted_required
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
