```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    rust_only_prepush:
      file_token_sets:
      - path: /scripts/ci_gate.sh
        required_tokens:
        - 'mode=critical: rust-only critical path'
        forbidden_tokens:
        - lane_python_parity
        - --impl python
        - expected critical|parity|fast
      - path: /.githooks/pre-push
        required_tokens:
        - make prepush
        forbidden_tokens:
        - --impl python
        - SPEC_PREPUSH_MODE=parity
      - path: /Makefile
        required_tokens:
        - SPEC_PREPUSH_MODE=critical ./scripts/ci_gate.sh
        forbidden_tokens:
        - 'python-parity:'
        - SPEC_PREPUSH_MODE=parity ./scripts/ci_gate.sh
    check:
      profile: governance.scan
      config:
        check: runtime.required_lane_only_prepush_required
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
  - id: DCGOV-RUNTIME-PREPUSH-006
    title: prepush path is rust-only
    purpose: Ensures prepush entrypoints and hook routing remain rust-only.
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
  - id: act.gov.runtime.rust.only.prepus.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.rust.only.prepus.1
  consumes:
  - act.gov.runtime.rust.only.prepus.1
```
