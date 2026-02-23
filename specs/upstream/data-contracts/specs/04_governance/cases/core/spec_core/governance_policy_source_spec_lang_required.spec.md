```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-POLICY-SRC-001
    title: policy source is spec-lang
    purpose: Ensures control-plane policy source contract states spec-lang as the policy verdict authority.
    harness:
      root: "."
      policy_source_contract:
        path: "/specs/02_contracts/28_spec_lang_policy_execution.md"
        required_tokens:
        - Policy verdict logic MUST be encoded
        - Shell scripts MUST NOT be the source of final policy verdict semantics
      check:
        profile: governance.scan
        config:
          check: governance.policy_source_spec_lang_required
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
