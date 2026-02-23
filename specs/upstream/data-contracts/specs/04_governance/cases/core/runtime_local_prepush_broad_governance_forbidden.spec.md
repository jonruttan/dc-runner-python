```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    local_prepush_broad_forbidden:
      path: /scripts/ci_gate.sh
      required_tokens:
      - skip broad governance (set SPEC_PREPUSH_REQUIRE_BROAD=1 to enable)
      - SPEC_PREPUSH_REQUIRE_BROAD=1
      forbidden_tokens:
      - run_step governance "${SPEC_RUNNER_BIN}" governance
    check:
      profile: governance.scan
      config:
        check: runtime.local_prepush_broad_governance_forbidden
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
  - id: DCGOV-RUNTIME-TRIAGE-009
    title: local prepush does not require broad governance
    purpose: Ensures local parity flow keeps broad governance out of default prepush
      path.
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
  - id: act.gov.runtime.local.prepush.br.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.local.prepush.br.1
  consumes:
  - act.gov.runtime.local.prepush.br.1
```
