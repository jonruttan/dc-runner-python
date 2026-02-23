# PHP Spec Runner Portability Cases

## DCIMPL-PHP-PORT-001

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
        - echo port-shell-ok
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-PORT-001
    title: shell command via sh -c works when shell exists
    purpose: Captures a shell-based cli.run case to detect environments where sh is
      unavailable.
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
          - port-shell-ok
        required: true
```

## DCIMPL-PHP-PORT-002

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
      X_PORT_BOOL: 'true'
      X_PORT_NUM: '7'
    check:
      profile: exec.command
      config:
        argv:
        - echo x:$X_PORT_BOOL y:$X_PORT_NUM
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PHP-PORT-002
    title: process env passthrough remains stringly typed
    purpose: Verifies env values passed through cli.run are observed as strings by
      child processes.
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
          - x:true y:7
        required: true
```

## DCIMPL-PHP-PORT-003

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
  - id: DCIMPL-PHP-PORT-003
    title: relative stdout path resolves from runner cwd
    purpose: Detects portability differences in cwd/path handling for stdout_path
      assertions.
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
```
