```yaml contract-spec
id: DCGOV-DOCS-REF-024
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: guide to contract links are valid
purpose: Ensures chapter 90 includes guide-to-contract mapping for the canonical guide set.
type: contract.check
harness:
  root: .
  reference_guide:
    path: /docs/book/90_reference_guide.md
    required_tokens:
    - Guide To Contract Map
    - guide_01_onboarding.md
    - guide_10_reference_navigation_patterns.md
    - specs/contract/10_docs_quality.md
    - specs/contract/27_runner_status_exchange.md
  check:
    profile: governance.scan
    config:
      check: docs.guide_contract_links_valid
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
