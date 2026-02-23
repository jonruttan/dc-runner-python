```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    git_hook_prepush:
      hook_path: /.githooks/pre-push
      install_script: /scripts/ci_gate.sh
      makefile_path: /Makefile
    check:
      profile: governance.scan
      config:
        check: runtime.git_hook_prepush_enforced
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
  - id: DCGOV-RUNTIME-PREPUSH-003
    title: managed pre-push hook enforces local parity gate
    purpose: Ensures repository-managed pre-push hook exists and is installable via
      canonical script.
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
  - id: act.gov.runtime.git.hook.prepush.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.git.hook.prepush.1
  consumes:
  - act.gov.runtime.git.hook.prepush.1
```
