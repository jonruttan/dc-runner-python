```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: governance.scan
      config:
        check: runtime.contract_step_asserts_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CONTRACT-STEP-001
    title: contract steps must declare asserts
    purpose: Enforces step-form contract nodes to use asserts list and non-empty children.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.check_profile_governance_scan_config_check_runtime_contract_step_asserts_required
  actions:
  - id: act.gov.runtime.contract.step.as.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.contract.step.as.1
  consumes:
  - act.gov.runtime.contract.step.as.1
```
