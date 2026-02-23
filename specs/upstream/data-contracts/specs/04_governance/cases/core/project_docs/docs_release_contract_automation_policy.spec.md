```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    release_contract:
      files:
      - docs/release_checklist.md
      required_tokens:
      - Release readiness is defined by executable gates, not manual checklists.
      - make ci-smoke
      - ./scripts/ci_gate.sh
      - convert it into an executable
      forbidden_patterns:
      - (?m)^##\s+[0-9]+\)
      - (?m)^\s*[0-9]+\.\s+(Run|Then|Check|Inspect)\b
    check:
      profile: governance.scan
      config:
        check: docs.release_contract_automation_policy
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
  - id: DCGOV-DOCS-QUAL-009
    title: release contract forbids manual sequential checklist choreography
    purpose: Ensures release guidance uses executable gate entrypoints and codifies
      that manual do-X-then-inspect-Y sequences are an anti-pattern.
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
      - id: assert_2
        assert:
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - docs.release_contract_automation_policy
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.release.contract.au.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.release.contract.au.1
  consumes:
  - act.gov.docs.release.contract.au.1
```
