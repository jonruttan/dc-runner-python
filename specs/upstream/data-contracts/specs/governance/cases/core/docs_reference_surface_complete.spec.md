# Governance Cases

## DCGOV-DOCS-REF-001

```yaml contract-spec
id: DCGOV-DOCS-REF-001
title: docs reference surface files exist
purpose: Enforces that the canonical docs reference surface remains complete and cannot silently
  lose required files.
type: contract.check
harness:
  root: .
  docs_reference_surface:
    required_files:
    - docs/book/reference_index.md
    - specs/schema/schema_v1.md
    - specs/contract/10_docs_quality.md
    - docs/book/10_getting_started.md
    - docs/book/20_case_model.md
    - docs/book/30_assertion_model.md
    - docs/book/40_spec_lang_authoring.md
    - docs/book/50_library_authoring.md
    - docs/book/60_runner_and_gates.md
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
    - specs/contract/*.md
  check:
    profile: governance.scan
    config:
      check: docs.reference_surface_complete
  use:
  - ref: /specs/libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.reference_surface_complete
    imports:
    - from: artifact
      names:
      - summary_json
```
