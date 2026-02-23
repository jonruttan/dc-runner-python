```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    ci_artifact_upload:
      path: /.github/workflows/ci.yml
      required_tokens:
      - actions/upload-artifact@v4
      - .artifacts/**
      - 'if: always()'
    check:
      profile: governance.scan
      config:
        check: runtime.ci_artifact_upload_paths_valid
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
  - id: DCGOV-RUNTIME-TRIAGE-013
    title: ci workflow uploads artifacts from canonical .artifacts path
    purpose: Ensures CI uploads gate and triage artifacts using a recursive .artifacts
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
  - id: act.gov.runtime.ci.artifact.uplo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.ci.artifact.uplo.1
  consumes:
  - act.gov.runtime.ci.artifact.uplo.1
```
