# Governance Cases

## DCGOV-DOCS-REF-005

```yaml contract-spec
id: DCGOV-DOCS-REF-005
title: runner cli flags are documented in development and impl docs
purpose: Prevents CLI contract drift by requiring script flags to be documented in the development
  guide and implementation reference pages.
type: contract.check
harness:
  root: .
  cli_docs:
    python_scripts:
    - dc-runner-python
    php_scripts:
    - dc-runner-php
    - dc-runner-php
    python_docs:
    - docs/development.md
    - dc-runner-python
    php_docs:
    - docs/development.md
    - dc-runner-php
  check:
    profile: governance.scan
    config:
      check: docs.cli_flags_documented
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
      - docs.cli_flags_documented
    imports:
    - from: artifact
      names:
      - summary_json
```
