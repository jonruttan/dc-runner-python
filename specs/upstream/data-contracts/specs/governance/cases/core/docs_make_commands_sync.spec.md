# Governance Cases

## DCGOV-DOCS-REF-007

```yaml contract-spec
id: DCGOV-DOCS-REF-007
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: docs use canonical make command entrypoints
purpose: Keeps contributor docs aligned on the canonical make-based command entrypoints for
  verification and gate execution.
type: contract.check
harness:
  root: .
  make_commands:
    files:
    - README.md
    - docs/development.md
    - .github/pull_request_template.md
    required_tokens:
    - make verify-docs
    - make core-check
    - make check
    - make prepush
    - make prepush-fast
    - make ci-cleanroom
    forbidden_tokens:
    - make prepush-parity
  check:
    profile: governance.scan
    config:
      check: docs.make_commands_sync
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
      - docs.make_commands_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
