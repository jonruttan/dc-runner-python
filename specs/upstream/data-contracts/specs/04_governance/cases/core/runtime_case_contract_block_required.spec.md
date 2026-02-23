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
        check: runtime.case_contract_block_required
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CONTRACT-BLOCK-001
    title: cases must use contract block
    purpose: Enforces top-level contract block requirement for executable cases.
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
- type: beta.check_profile_governance_scan_config_check_runtime_case_contract_block_required
  actions:
  - id: act.gov.runtime.case.contract.bl.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.case.contract.bl.1
  consumes:
  - act.gov.runtime.case.contract.bl.1
```
