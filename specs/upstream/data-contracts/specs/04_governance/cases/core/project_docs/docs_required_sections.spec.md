```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    required_sections:
      docs/book/05_what_is_data_contracts.md:
      - '## System Intent'
      - '## High-Level Architecture'
      - '## Why This Exists'
      docs/book/15_spec_lifecycle.md:
      - '## Lifecycle Flow'
      - '## Feedback Loop'
      docs/book/20_case_model.md:
      - '## Canonical Top-Level Topology'
      - '## Responsibility Split'
      - '## Contract Form'
      - '## Normative References'
      docs/book/25_system_topology.md:
      - '## Component Topology'
      - '## Ownership Topology'
      docs/book/30_assertion_model.md:
      - '## Canonical Contract Shape'
      - '## Imports and Precedence'
      - '## Forbidden canonical Forms'
      - '## Group Semantics'
      docs/book/35_usage_guides_index.md:
      - '## Guide Paths'
      docs/book/90_reference_guide.md:
      - '## Normative Sources'
      - '## Guide To Contract Map'
      - '## Generated References'
      docs/book/guides/index.md:
      - '## Guide Set'
      docs/book/guides/guide_01_onboarding.md:
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_02_first_spec_authoring.md:
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_03_running_checks_and_gates.md:
      - '## Gate Execution Flow'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_04_debugging_failures.md:
      - '## Troubleshooting Decision Tree'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_05_release_and_change_control.md:
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_06_governance_tuning.md:
      - '## Governance Decision Path'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_07_schema_extension_workflow.md:
      - '## Schema Evolution Flow'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_08_ci_integration.md:
      - '## CI Flow'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_09_status_exchange_operations.md:
      - '## Status Exchange Flow'
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/guides/guide_10_reference_navigation_patterns.md:
      - '## Do This Now'
      - '## How To Verify Success'
      - '## Common Failure Signatures'
      docs/book/reference_index.md:
      - '# Reference Index'
      - Canonical order for reference-manual chapters.
      - how to use
      docs/book/40_spec_lang_authoring.md:
      - '## Mapping-AST Rules'
      - '## Readability Patterns'
      - '## Anti-Patterns'
      - '## Library-Backed Reuse'
      docs/book/60_runner_and_gates.md:
      - '## required lane'
      - '## Gate Sequence'
      - '## Exit Code Semantics'
      - '## Compatibility (Non-Blocking)'
      docs/book/80_troubleshooting.md:
      - '## Failure Taxonomy'
      - '## Deterministic Recovery Flow'
      - '## Escalation'
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
    purpose: Keeps the core reference pages structurally complete by requiring stable
      section tokens for author and implementer workflows.
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
