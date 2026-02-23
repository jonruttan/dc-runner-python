```yaml contract-spec
id: DCGOV-RUNTIME-CORE-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: non-core scripts absent from active policy and traceability
purpose: Ensures policy and traceability surfaces do not reference retired script entrypoints.
type: contract.check
harness:
  root: .
  policy_traceability_paths:
    - /specs/02_contracts/policy_v1.yaml
    - /specs/02_contracts/traceability_v1.yaml
  forbidden_tokens:
    - scripts/core_gate.sh
    - scripts/local_ci_parity.sh
    - scripts/docs_doctor.sh
    - scripts/install_git_hooks.sh
    - scripts/prepush_gate.sh
  check:
    profile: governance.scan
    config:
      check: runtime.non_core_scripts_not_in_active_policy_traceability
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
