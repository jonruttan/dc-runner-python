# Governance Cases

## DCGOV-RUNTIME-ASSERT-001

```yaml contract-spec
id: DCGOV-RUNTIME-ASSERT-001
title: runtime assertion paths compile and evaluate through spec-lang
purpose: Enforces that runner assertion semantics route through spec-lang expression evaluation
  and avoid direct ad-hoc contain or regex execution paths.
type: contract.check
harness:
  root: .
  assert_engine:
    files:
    - path: /dc-runner-php
      required_tokens:
      - compileAssertionLeafExpr(
      - assertLeafPredicate(
      - specLangEvalPredicate(
      forbidden_tokens:
      - strpos($subject, $v)
      - preg_match('/' . str_replace('/', '\/', $v) . '/u', $subject)
    - path: /dc-runner-php
      required_tokens:
      - compileAssertionLeafExpr(
      - assertLeafPredicate(
      - specLangEvalPredicate(
      forbidden_tokens:
      - strpos($subject, $v)
      - preg_match('/' . str_replace('/', '\/', $v) . '/u', $subject)
    - path: /dc-runner-python
      required_tokens:
      - eval_predicate(
      forbidden_tokens:
      - assert_text_op(
    - path: /dc-runner-python
      required_tokens:
      - evaluate_internal_assert_tree(
      - eval_predicate(
      forbidden_tokens:
      - def assert_text_op(
    - path: /dc-runner-python
      required_tokens:
      - run_assertions_with_context(
      forbidden_tokens:
      - contain assertion failed
    - path: /dc-runner-python
      required_tokens:
      - run_assertions_with_context(
      forbidden_tokens:
      - contain assertion failed
    - path: /dc-runner-python
      required_tokens:
      - run_assertions_with_context(
      forbidden_tokens:
      - contain assertion failed
  check:
    profile: governance.scan
    config:
      check: runtime.assertions_via_spec_lang
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
      - runtime.assertions_via_spec_lang
    imports:
    - from: artifact
      names:
      - summary_json
```
