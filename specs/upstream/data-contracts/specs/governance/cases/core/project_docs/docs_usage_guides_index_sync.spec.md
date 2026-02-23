```yaml contract-spec
id: DCGOV-DOCS-REF-020
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: usage guides index is synchronized
purpose: Ensures the guides index includes the canonical guide set.
type: contract.check
harness:
  root: .
  docs_guides_index:
    path: /docs/book/guides/index.md
    required_paths:
    - /docs/book/guides/guide_01_onboarding.md
    - /docs/book/guides/guide_02_first_spec_authoring.md
    - /docs/book/guides/guide_03_running_checks_and_gates.md
    - /docs/book/guides/guide_04_debugging_failures.md
    - /docs/book/guides/guide_05_release_and_change_control.md
    - /docs/book/guides/guide_06_governance_tuning.md
    - /docs/book/guides/guide_07_schema_extension_workflow.md
    - /docs/book/guides/guide_08_ci_integration.md
    - /docs/book/guides/guide_09_status_exchange_operations.md
    - /docs/book/guides/guide_10_reference_navigation_patterns.md
  check:
    profile: governance.scan
    config:
      check: docs.usage_guides_index_sync
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
```
