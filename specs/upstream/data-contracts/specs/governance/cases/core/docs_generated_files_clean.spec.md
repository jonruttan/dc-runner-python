# Governance Cases

## DCGOV-DOCS-QUAL-008

```yaml contract-spec
id: DCGOV-DOCS-QUAL-008
title: generated docs artifacts are up-to-date
purpose: Ensures generated reference index, coverage, and docs graph artifacts are kept fresh.
type: contract.check
harness:
  root: .
  docs_quality:
    manifest: docs/book/reference_manifest.yaml
    index_out: /docs/book/reference_index.md
    coverage_out: /docs/book/reference_coverage.md
    graph_out: /docs/book/docs_graph.json
  check:
    profile: governance.scan
    config:
      check: docs.generated_files_clean
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
      - docs.generated_files_clean
    imports:
    - from: artifact
      names:
      - summary_json
```
