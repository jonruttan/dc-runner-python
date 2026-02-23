```yaml contract-spec
id: DCGOV-RUNTIME-TRIAGE-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: governance triage entrypoint exists with required surface
purpose: Ensures canonical governance triage script exists and exposes required flags.
type: contract.check
harness:
  root: .
  governance_triage:
    path: /scripts/governance_triage.sh
    required_tokens:
    - --mode auto
    - --mode auto|targeted|broad-first
    - --from-failures
    - --check-prefix
    - --check-id
    - .artifacts/governance-triage.json
    - .artifacts/governance-triage-summary.md
  check:
    profile: governance.scan
    config:
      check: runtime.governance_triage_entrypoint_required
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
