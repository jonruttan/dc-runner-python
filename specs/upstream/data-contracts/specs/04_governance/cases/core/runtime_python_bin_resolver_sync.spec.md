```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    python_bin_resolver:
      helper: scripts/lib/python_bin.sh
      files:
      - scripts/lib/python_bin.sh
      required_tokens:
      - resolve_python_bin() {
      - ${root_dir}/.venv/bin/python
      - ${root_dir}/../../.venv/bin/python
      - python3
      forbidden_tokens: []
    check:
      profile: governance.scan
      config:
        check: runtime.compatibility_python_lane_bin_resolver_sync
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
  - id: DCGOV-RUNTIME-CONFIG-002
    title: python-invoking adapter scripts use shared python-bin resolver helper
    purpose: Keeps shared Python resolver helper contract stable for remaining tooling
      paths.
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
          - runtime.compatibility_python_lane_bin_resolver_sync
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.python.bin.resol.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.python.bin.resol.1
  consumes:
  - act.gov.runtime.python.bin.resol.1
```
