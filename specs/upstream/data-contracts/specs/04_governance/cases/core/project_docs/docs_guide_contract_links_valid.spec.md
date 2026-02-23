```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    reference_guide:
      path: /docs/book/90_reference_guide.md
      required_tokens:
      - Guide To Contract Map
      - guide_01_onboarding.md
      - guide_10_reference_navigation_patterns.md
      - specs/02_contracts/10_docs_quality.md
      - specs/02_contracts/27_runner_status_exchange.md
    check:
      profile: governance.scan
      config:
        check: docs.guide_contract_links_valid
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-024
    title: guide to contract links are valid
    purpose: Ensures chapter 90 includes guide-to-contract mapping for the canonical
      guide set.
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
  - id: act.gov.docs.guide.contract.link.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.guide.contract.link.1
  consumes:
  - act.gov.docs.guide.contract.link.1
```
