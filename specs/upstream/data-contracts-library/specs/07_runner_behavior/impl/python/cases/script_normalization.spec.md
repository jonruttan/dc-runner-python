# Python Script CLI Cases: Normalization

## DCIMPL-PY-SCRIPT-NORM-001

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
    entrypoint: spec_runner.script_entrypoints:normalize_docs_layout_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-NORM-001
    title: normalize_docs_layout help renders usage
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
          - --profile
        required: true
```

## DCIMPL-PY-SCRIPT-NORM-002

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
    entrypoint: spec_runner.script_entrypoints:normalize_docs_layout_main
    check:
      profile: exec.command
      config:
        argv:
        - --check
        - --write
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-NORM-002
    title: normalize_docs_layout rejects conflicting modes
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
          - not allowed with argument
        required: true
```

## DCIMPL-PY-SCRIPT-NORM-003

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
    entrypoint: spec_runner.script_entrypoints:normalize_repo_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-NORM-003
    title: normalize_repo help renders usage
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
          - --scope
        required: true
```

## DCIMPL-PY-SCRIPT-NORM-004

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
    entrypoint: spec_runner.script_entrypoints:normalize_repo_main
    check:
      profile: exec.command
      config:
        argv:
        - --check
        - --scope
        - bad
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-NORM-004
    title: normalize_repo rejects invalid scope
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
          - invalid choice
        required: true
```
