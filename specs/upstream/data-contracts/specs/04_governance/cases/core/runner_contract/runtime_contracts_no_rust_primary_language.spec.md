```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    contract_language:
      files:
      - /specs/02_contracts/10_docs_quality.md
      - /specs/02_contracts/12_runner_interface.md
      - /specs/02_contracts/25_compatibility_matrix.md
      forbidden_tokens:
      - implementation-agnostic
      - required lane
    check:
      profile: governance.scan
      config:
        check: runtime.contracts_no_rust_primary_language
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CONTRACT-001
    title: contracts avoid rust-primary language
    purpose: Ensures active contracts remain implementation-agnostic.
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
- type: beta.scan
  actions:
  - id: act.gov.runtime.contracts.no.rus.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.contracts.no.rus.1
  consumes:
  - act.gov.runtime.contracts.no.rus.1
```
