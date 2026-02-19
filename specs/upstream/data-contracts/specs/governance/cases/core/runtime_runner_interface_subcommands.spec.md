# Governance Cases

## DCGOV-RUNTIME-CONFIG-004

```yaml contract-spec
id: DCGOV-RUNTIME-CONFIG-004
title: rust runner adapter declares required interface subcommands
purpose: Ensures the Rust runner adapter exposes the required runner interface subcommand
  labels.
type: contract.check
harness:
  root: .
  runner_interface_subcommands:
    path: /dc-runner-rust
    required_subcommands:
    - governance
    - style-check
    - normalize-check
    - normalize-fix
    - schema-registry-check
    - schema-registry-build
    - schema-docs-check
    - schema-docs-build
    - lint
    - typecheck
    - compilecheck
    - conformance-purpose-json
    - conformance-purpose-md
    - spec-portability-json
    - spec-portability-md
    - runner-independence-json
    - runner-independence-md
    - python-dependency-json
    - python-dependency-md
    - ci-gate-summary
    - docs-build
    - docs-build-check
    - docs-lint
    - docs-graph
    - conformance-parity
    - runner-certify
    - test-core
    - test-full
  check:
    profile: governance.scan
    config:
      check: runtime.runner_interface_subcommands
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
      - runtime.runner_interface_subcommands
    imports:
    - from: artifact
      names:
      - summary_json
```
