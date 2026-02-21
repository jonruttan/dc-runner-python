```yaml contract-spec
id: DCGOV-RUNTIME-DOCS-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docs use control-plane language
purpose: Ensures active docs describe this repository as implementation-agnostic control-plane.
type: contract.check
harness:
  root: .
  docs_language:
    files:
    - /README.md
    - /docs/development.md
    - /docs/book/index.md
    - /docs/book/60_runner_and_gates.md
    required_tokens:
    - implementation-agnostic control plane
    - runtime execution ownership lives in runner repositories
  check:
    profile: governance.scan
    config:
      check: runtime.docs_no_required_lane_language
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
