```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    required_sections:
      docs/book/index.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/05_what_is_data_contracts.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/10_getting_started.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/15_spec_lifecycle.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/20_case_model.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/25_system_topology.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/30_assertion_model.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/35_usage_guides_index.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/40_spec_lang_authoring.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/50_library_authoring.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/60_runner_and_gates.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/65_runner_status_and_compatibility.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/70_governance_and_quality.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/80_troubleshooting.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/90_reference_guide.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      - Guide To Contract Map
      docs/book/99_generated_reference_index.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/reference_index.md:
      - '# Reference Index'
      - Canonical order for reference-manual chapters.
      docs/book/guides/index.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_01_onboarding.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_02_first_spec_authoring.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_03_running_checks_and_gates.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_04_debugging_failures.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_05_release_and_change_control.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_06_governance_tuning.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_07_schema_extension_workflow.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_08_ci_integration.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_09_status_exchange_operations.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
      docs/book/guides/guide_10_reference_navigation_patterns.md:
      - '## When to read this'
      - '## What you will do'
      - '## Step-by-step'
      - '## Common failure signals'
      - '## Normative refs'
    check:
      profile: governance.scan
      config:
        check: docs.required_sections
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
  - id: DCGOV-DOCS-REF-003
    title: key reference chapters include required sections
    purpose: Keeps docs chapters structurally consistent with tutorial-first format.
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
          - docs.required_sections
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.required.sections.s.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.required.sections.s.1
  consumes:
  - act.gov.docs.required.sections.s.1
```
