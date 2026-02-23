```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-RUNTIME-SHELL-002
    title: extractor artifact compatibility preserved
    purpose: Ensures extractor scripts keep canonical artifact file paths and key names stable.
    harness:
      root: "."
      extractor_script:
        path: "/scripts/governance_catalog_validate.sh"
        required_tokens:
        - ".artifacts/governance-catalog-validate.json"
        - duplicate_case_id_count
        - unmapped_case_check_count
      check:
        profile: governance.scan
        config:
          check: runtime.artifact_contract_compatibility_preserved
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
```
