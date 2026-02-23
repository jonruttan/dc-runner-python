```yaml contract-spec
id: DCGOV-PIPE-OPTIONAL-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: optional report pipeline is chained
purpose: Ensures optional profile reporting surfaces are linked as chain steps and artifact outputs remain coherent.
type: contract.check
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: governance.optional_pipeline_chain_valid
  chain:
    fail_fast: true
    steps:
      - id: step_optional_artifact_emit
        class: must
        ref: /specs/governance/cases/core/runtime_matrix_artifacts_emitted.spec.md#DCGOV-RUNTIME-CI-003
      - id: step_optional_status_ingest_job
        class: can
        ref: /specs/governance/cases/core/runner_contract/runtime_status_ingest_job_present.spec.md#DCGOV-RUNTIME-CI-002
      - id: step_optional_docs_links
        class: can
        ref: /specs/governance/cases/core/project_docs/docs_usage_guides_index_sync.spec.md#DCGOV-DOCS-REF-020
  use:
    - ref: /specs/05_libraries/policy/policy_ci_gate.spec.md#LIB-POLICY-CI-001
      as: lib_policy_ci
      symbols:
        - policy.ci.optional_profile_report_only
        - policy.ci.artifacts_present
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names:
        - violation_count
        - context_json
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
    - id: assert_2
      assert:
        - call:
            - {var: policy.ci.optional_profile_report_only}
            - std.object.get:
                - {var: context_json}
                - governance_optional_report
        - call:
            - {var: policy.ci.artifacts_present}
            - std.object.get:
                - {var: context_json}
                - governance_optional_report
```
