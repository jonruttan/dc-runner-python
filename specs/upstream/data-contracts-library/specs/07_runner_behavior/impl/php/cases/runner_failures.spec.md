# PHP Spec Runner Expected Failure Cases

## DCIMPL-PHP-RUN-F001

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
    check:
      profile: read.text
      config:
        path: /tmp/not-allowed.txt
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F001
    title: text.file virtual absolute path missing file fails runtime
    purpose: Verifies virtual-root absolute paths resolve under contract root and
      fail at runtime when the file is missing.
    expect:
      portable:
        status: fail
        category: runtime
        message_tokens:
        - cannot read fixture file
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - x
        required: true
```

## DCIMPL-PHP-RUN-F002

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
    check:
      profile: read.text
      config:
        path: ../../../../../../outside.txt
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F002
    title: text.file path escape is rejected
    purpose: Verifies text.file rejects relative paths that escape the contract root
      boundary.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - text.file path escapes contract root
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - outside
        required: true
```

## DCIMPL-PHP-RUN-F003

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
    check:
      profile: exec.command
      config:
        argv:
        - x
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F003
    title: cli.run without entrypoint fails
    purpose: Verifies cli.run reports runtime failure when no entrypoint source is
      available.
    expect:
      portable:
        status: fail
        category: runtime
        message_tokens:
        - requires explicit harness.entrypoint
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
          - x
        required: true
```

## DCIMPL-PHP-RUN-F004

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
        - '{}'
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F004
    title: cli.run rejects unknown spec-lang symbol usage
    purpose: Verifies unknown expression symbols are rejected as schema failures.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - unsupported spec_lang symbol
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
          not.a.real.symbol:
          - var: stdout
        required: true
```

## DCIMPL-PHP-RUN-F005

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
    entrypoint: /bin/sh -c
    check:
      profile: exec.command
      config:
        argv:
        - exit 2
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F005
    title: cli.run exit_code mismatch is assertion failure
    purpose: Verifies cli.run reports assertion failure when observed exit code differs
      from expected.
    expect:
      portable:
        status: fail
        category: assertion
        message_tokens:
        - exit_code expected=0 actual=2
    asserts:
      checks: []
```

## DCIMPL-PHP-RUN-F006

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config: {}
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F006
    title: unknown type reports runtime failure
    purpose: Verifies unknown contract-spec types are reported as runtime failures.
    expect:
      portable:
        status: fail
        category: runtime
        message_tokens:
        - unknown contract-spec type
    asserts:
      checks: []
```

## DCIMPL-PHP-RUN-F007

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
    stdin_text: nope
    check:
      profile: exec.command
      config:
        argv:
        - x
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F007
    title: cli.run rejects unsupported harness keys
    purpose: Verifies cli.run validates supported harness keys and rejects unknown
      ones.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - unsupported harness key(s)
    asserts:
      checks: []
```

## DCIMPL-PHP-RUN-F008

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
    check:
      profile: read.text
      config:
        path: /fixtures/sample.txt
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-F008
    title: leaf target key is rejected
    purpose: Verifies leaf assertions including target key are rejected as schema
      violations.
    expect:
      portable:
        status: fail
        category: schema
        message_tokens:
        - 'leaf assertion must not include key: target'
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
          lit:
            target: text
            contain:
            - fixture-content
        required: true
```
