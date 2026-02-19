# Governance Cases

## DCGOV-RUNTIME-TRIAGE-008

```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-008
title: governance triage auto mode is targeted-first by default
purpose: Ensures triage auto mode resolves to targeted-first and exposes broad-first as an
  explicit mode.
type: contract.check
harness:
  root: .
  triage_targeted_first:
    path: /scripts/governance_triage.sh
    required_tokens:
    - TRIAGE_MODE_DEFAULT
    - targeted-first
    - broad-first
    - resolve_targeted_prefixes
    - selection_source
  check:
    profile: governance.scan
    config:
      check: runtime.governance_triage_targeted_first_required
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
