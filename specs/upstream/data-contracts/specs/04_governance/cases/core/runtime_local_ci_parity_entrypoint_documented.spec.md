```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    local_ci_parity_docs:
      files:
      - /README.md
      - /docs/development.md
      - /docs/book/60_runner_and_gates.md
      - /docs/book/80_troubleshooting.md
      required_tokens:
      - make prepush
      - make prepush-fast
      - make hooks-install
      - SPEC_PREPUSH_BYPASS=1
    check:
      profile: governance.scan
      config:
        check: runtime.local_ci_parity_entrypoint_documented
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
  - id: DCGOV-RUNTIME-PREPUSH-005
    title: local ci parity entrypoint is documented for contributors
    purpose: Ensures contributor docs cover parity-default prepush, fast opt-out,
      and hook installation.
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
  - id: act.gov.runtime.local.ci.parity.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.local.ci.parity.1
  consumes:
  - act.gov.runtime.local.ci.parity.1
```
