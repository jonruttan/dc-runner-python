# PHP Spec Runner Pass Cases

## DCIMPL-PHP-RUN-001

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
      config: {}
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-001
    title: text.file default target uses containing spec file
    purpose: Verifies text.file reads the containing spec document when path is omitted.
    expect:
      portable:
        status: pass
        category: null
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
          - '# PHP Spec Runner Pass Cases'
        required: true
```

## DCIMPL-PHP-RUN-002

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
  - id: DCIMPL-PHP-RUN-002
    title: text.file supports relative path
    purpose: Verifies text.file can read a relative path under the same repository
      root.
    expect:
      portable:
        status: pass
        category: null
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
          - fixture-content
        required: true
```

## DCIMPL-PHP-RUN-003

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
  - id: DCIMPL-PHP-RUN-003
    title: text.file can group succeeds with one passing branch
    purpose: Ensures can group semantics pass when at least one branch evaluates true.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - no-match-token
          - fixture-content
        required: false
```

## DCIMPL-PHP-RUN-004

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
        - hello-runner
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-004
    title: cli.run explicit entrypoint executes argv
    purpose: Verifies cli.run executes explicit harness entrypoint with argv arguments.
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
          std.string.contains:
          - var: stdout
          - hello-runner
        required: true
```

## DCIMPL-PHP-RUN-005

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
    env:
      X_PHP_SPEC: 'on'
    check:
      profile: exec.command
      config:
        argv:
        - echo $X_PHP_SPEC
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-005
    title: cli.run applies harness env mapping
    purpose: Verifies cli.run applies harness env values to the subprocess environment.
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
          std.string.contains:
          - var: stdout
          - 'on'
        required: true
```

## DCIMPL-PHP-RUN-006

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
        - fallback-ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-006
    title: cli.run requires explicit harness entrypoint
    purpose: Verifies cli.run executes when harness entrypoint is explicitly provided.
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
          std.string.contains:
          - var: stdout
          - fallback-ok
        required: true
```

## DCIMPL-PHP-RUN-007

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
        - '[]'
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-007
    title: cli.run json_type list assertion passes
    purpose: Verifies json parsing and type checks can be expressed via std.* mapping-AST.
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
          std.type.json_type:
          - std.json.parse:
            - var: stdout
          - list
        required: true
```

## DCIMPL-PHP-RUN-008

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
        - echo runner-err 1>&2
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-008
    title: cli.run can assert stderr output
    purpose: Verifies stderr target assertions using a command that writes to stderr.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - stderr
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: stderr
          - runner-err
        required: true
```

## DCIMPL-PHP-RUN-009

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
        - specs/07_runner_behavior/impl/php/cases/fixtures/path_target.txt
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-009
    title: cli.run supports stdout_path and stdout_path_text targets
    purpose: Verifies path-based assertions for stdout_path existence and stdout_path_text
      content.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - stdout_path
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: stdout_path
          - path_target.txt
        required: true
      - id: assert_2
        assert:
          std.string.contains:
          - var: stdout_path_text
          - path target file content
        imports:
        - from: artifact
          names:
          - stdout_path_text
        required: true
```
