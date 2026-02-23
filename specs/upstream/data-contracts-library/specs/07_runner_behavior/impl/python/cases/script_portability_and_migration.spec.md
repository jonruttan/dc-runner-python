# Python Script CLI Cases: Portability and Migration

## DCIMPL-PY-SCRIPT-PORT-001

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
    entrypoint: spec_runner.script_entrypoints:spec_portability_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --out
        - .artifacts/spec-portability-script-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-001
    title: spec_portability_report writes json artifact
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
          - wrote .artifacts/spec-portability-script-case.json
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-002

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
    entrypoint: spec_runner.script_entrypoints:spec_portability_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - nope
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-002
    title: spec_portability_report rejects invalid format
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

## DCIMPL-PY-SCRIPT-PORT-003

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
    entrypoint: spec_runner.script_entrypoints:impl_evaluate_migration_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-003
    title: impl evaluate migration report help renders usage
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
          - --cases
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-004

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
    entrypoint: spec_runner.script_entrypoints:impl_evaluate_migration_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --unknown-option
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-004
    title: impl evaluate migration report rejects invalid option
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
          - unrecognized arguments
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-005

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
    entrypoint: spec_runner.script_entrypoints:split_library_cases_per_symbol_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-005
    title: split library cases command help renders usage
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
          - --write
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-006

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
    entrypoint: spec_runner.script_entrypoints:split_library_cases_per_symbol_main
    check:
      profile: exec.command
      config:
        argv: []
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-006
    title: split library cases command requires input paths
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
          - paths
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-007

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
    entrypoint: spec_runner.script_entrypoints:conformance_purpose_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --out
        - .artifacts/conformance-purpose-script-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-007
    title: conformance purpose report writes json artifact
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
          - wrote .artifacts/conformance-purpose-script-case.json
        required: true
```

## DCIMPL-PY-SCRIPT-PORT-008

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
    entrypoint: spec_runner.script_entrypoints:conformance_purpose_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - nope
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-PORT-008
    title: conformance purpose report rejects invalid format
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
