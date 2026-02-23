```yaml contract-spec
id: DCGOV-PIPE-SHELL-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: shell extractors are fact emitters only
purpose: Ensures extractor scripts do not emit direct policy failure exits for governance domains.
type: contract.check
harness:
  root: .
  extractor_script:
    path: /scripts/governance_catalog_validate.sh
    must_not_contain:
      - exit 1
      - blocking_fail
  check:
    profile: governance.scan
    config:
      check: runtime.shell_extractors_fact_only_enforced
contract:
  defaults:
    class: MUST
  imports:
    - from: artifact
      names: [violation_count]
  steps:
    - id: assert_1
      assert:
        std.logic.eq:
          - {var: violation_count}
          - 0
```
