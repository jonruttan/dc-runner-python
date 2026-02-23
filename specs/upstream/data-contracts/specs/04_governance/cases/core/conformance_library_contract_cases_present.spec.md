```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    conformance_library_contract_cases_present:
      path: /specs/03_conformance/cases/core/spec_lang_library_contract.spec.md
      required_case_ids:
      - DCCONF-LIB-CONTRACT-001
      - DCCONF-LIB-CONTRACT-002
      - DCCONF-LIB-CONTRACT-003
    check:
      profile: governance.scan
      config:
        check: conformance.library_contract_cases_present
    use:
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-CONF-LIB-CONTRACT-001
    title: conformance library contract coverage cases are present
    purpose: Ensures conformance includes executable evaluate-based coverage for flat
      spec_lang.export defines contract behavior.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - conformance.library_contract_cases_present
adapters:
- type: beta.scan
  actions:
  - id: act.gov.conformance.library.cont.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.conformance.library.cont.1
  consumes:
  - act.gov.conformance.library.cont.1
```
