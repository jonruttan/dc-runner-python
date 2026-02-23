```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    make_python_parity:
      path: /Makefile
      required_tokens:
      - 'prepush: ## Required local pre-push gate (default rust critical-gate path)'
      - SPEC_PREPUSH_MODE=critical ./scripts/ci_gate.sh
      - 'prepush-fast: ## Rust-only critical pre-push mode'
      forbidden_tokens:
      - 'python-parity:'
      - --impl python
      - SPEC_PREPUSH_MODE=parity
    check:
      profile: governance.scan
      config:
        check: runtime.make_python_parity_targets_forbidden
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
  - id: DCGOV-RUNTIME-PREPUSH-002
    title: makefile contains no python parity prepush targets
    purpose: Ensures contributor-facing make targets do not expose python runner lane
      execution.
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
  - id: act.gov.runtime.make.python.pari.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.make.python.pari.1
  consumes:
  - act.gov.runtime.make.python.pari.1
```
