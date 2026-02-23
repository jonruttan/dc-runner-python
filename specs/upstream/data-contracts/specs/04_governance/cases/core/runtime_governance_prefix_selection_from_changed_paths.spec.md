```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    triage_prefix_selection:
      path: /scripts/governance_triage.sh
      required_tokens:
      - collect_changed_paths
      - select_prefixes_from_changed_paths
      - selection_source="changed_paths"
      - CHECK_PREFIXES
    check:
      profile: governance.scan
      config:
        check: runtime.governance_prefix_selection_from_changed_paths
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
  - id: DCGOV-RUNTIME-TRIAGE-011
    title: governance triage selects prefixes from changed paths
    purpose: Ensures triage auto mode derives targeted check prefixes from changed
      paths before fallback prefixes.
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
  - id: act.gov.runtime.governance.prefi.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.governance.prefi.1
  consumes:
  - act.gov.runtime.governance.prefi.1
```
