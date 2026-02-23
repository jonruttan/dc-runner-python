# PHP Spec Runner Assertion Health Cases

## DCIMPL-PHP-AH-001

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md
      as: lib_policy_text
      symbols:
      - policy.text.contains_pair
      - policy.text.contains_all
      - policy.text.contains_none
    entrypoint: /bin/echo
    check:
      profile: exec.command
      config:
        argv:
        - ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-AH-001
    title: cli.run warn mode emits diagnostics without failing
    purpose: Verifies assert_health warn mode on cli.run preserves pass outcome while
      emitting warnings.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: stdout
          - ok
          - ok
        required: true
```

## DCIMPL-PHP-AH-002

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md
      as: lib_policy_text
      symbols:
      - policy.text.contains_pair
      - policy.text.contains_all
      - policy.text.contains_none
    entrypoint: /bin/echo
    check:
      profile: exec.command
      config:
        argv:
        - ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-AH-002
    title: cli.run error mode fails on assertion-health diagnostics
    purpose: Verifies assert_health error mode on cli.run converts assertion-health
      findings into assertion failures.
    expect:
      portable:
        status: fail
        category: assertion
        message_tokens:
        - AH004
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: stdout
          - ok
          - ok
        required: true
```

## DCIMPL-PHP-AH-003

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md
      as: lib_policy_text
      symbols:
      - policy.text.contains_pair
      - policy.text.contains_all
      - policy.text.contains_none
    entrypoint: /bin/echo
    check:
      profile: exec.command
      config:
        argv:
        - ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-AH-003
    title: invalid assert_health mode is schema failure
    purpose: Verifies invalid assert_health mode values are rejected as schema errors.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - assert_health.mode must be one of
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: stdout
          - ok
        required: true
```

## DCIMPL-PHP-AH-004

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md
      as: lib_policy_text
      symbols:
      - policy.text.contains_pair
      - policy.text.contains_all
      - policy.text.contains_none
    entrypoint: /bin/echo
    check:
      profile: exec.command
      config:
        argv:
        - ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-AH-004
    title: global assert health mode applies when case mode is omitted
    purpose: Verifies SPEC_RUNNER_ASSERT_HEALTH controls diagnostics when assert_health.mode
      is not set in a case.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: stdout
          - ok
          - ok
        required: true
```

## DCIMPL-PHP-AH-005

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md
      as: lib_policy_text
      symbols:
      - policy.text.contains_pair
      - policy.text.contains_all
      - policy.text.contains_none
    entrypoint: /bin/echo
    check:
      profile: exec.command
      config:
        argv:
        - ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-AH-005
    title: per-case ignore overrides global warn policy
    purpose: Verifies assert_health.mode ignore suppresses diagnostics even when global
      policy is warn.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: stdout
          - ok
          - ok
        required: true
```
