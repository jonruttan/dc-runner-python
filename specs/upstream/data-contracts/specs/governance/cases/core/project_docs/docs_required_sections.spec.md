```yaml contract-spec
id: DCGOV-DOCS-REF-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: key reference chapters include required sections
purpose: Keeps the core reference pages structurally complete by requiring stable section
  tokens for author and implementer workflows.
type: contract.check
harness:
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
    - '## Forbidden prior Forms'
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
  - ref: /specs/05_libraries/policy/policy_core.spec.md
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
      - docs.required_sections
    imports:
    - from: artifact
      names:
      - summary_json
```
