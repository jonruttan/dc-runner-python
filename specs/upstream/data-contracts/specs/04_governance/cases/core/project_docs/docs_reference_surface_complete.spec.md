```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    docs_reference_surface:
      required_files:
      - docs/book/reference_index.md
      - specs/01_schema/schema_v1.md
      - specs/02_contracts/10_docs_quality.md
      - docs/book/05_what_is_data_contracts.md
      - docs/book/10_getting_started.md
      - docs/book/15_spec_lifecycle.md
      - docs/book/20_case_model.md
      - docs/book/25_system_topology.md
      - docs/book/30_assertion_model.md
      - docs/book/35_usage_guides_index.md
      - docs/book/guides/index.md
      - docs/book/guides/guide_01_onboarding.md
      - docs/book/guides/guide_02_first_spec_authoring.md
      - docs/book/guides/guide_03_running_checks_and_gates.md
      - docs/book/guides/guide_04_debugging_failures.md
      - docs/book/guides/guide_05_release_and_change_control.md
      - docs/book/guides/guide_06_governance_tuning.md
      - docs/book/guides/guide_07_schema_extension_workflow.md
      - docs/book/guides/guide_08_ci_integration.md
      - docs/book/guides/guide_09_status_exchange_operations.md
      - docs/book/guides/guide_10_reference_navigation_patterns.md
      - docs/book/40_spec_lang_authoring.md
      - docs/book/50_library_authoring.md
      - docs/book/60_runner_and_gates.md
      - docs/book/65_runner_status_and_compatibility.md
      - docs/book/70_governance_and_quality.md
      - docs/book/80_troubleshooting.md
      - docs/book/90_reference_guide.md
      - docs/book/99_generated_reference_index.md
      - docs/book/93_appendix_spec_lang_builtin_catalog.md
      - docs/book/93a_std_core.md
      - docs/book/93b_std_logic.md
      - docs/book/93c_std_math.md
      - docs/book/93d_std_string.md
      - docs/book/93e_std_collection.md
      - docs/book/93f_std_object.md
      - docs/book/93g_std_type.md
      - docs/book/93h_std_set.md
      - docs/book/93i_std_json_schema_fn_null.md
      - docs/book/93n_spec_case_templates_reference.md
      required_globs:
      - specs/02_contracts/*.md
    check:
      profile: governance.scan
      config:
        check: docs.reference_surface_complete
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
  - id: DCGOV-DOCS-REF-001
    title: docs reference surface files exist
    purpose: Enforces that the canonical docs reference surface remains complete and
      cannot silently lose required files.
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
          - docs.reference_surface_complete
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.reference.surface.c.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.reference.surface.c.1
  consumes:
  - act.gov.docs.reference.surface.c.1
```
