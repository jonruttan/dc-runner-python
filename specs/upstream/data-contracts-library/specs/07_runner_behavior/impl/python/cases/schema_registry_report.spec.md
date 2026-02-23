# Python Schema Registry Report Command Cases

## DCIMPL-PY-SCHEMA-REG-001

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
    entrypoint: spec_runner.spec_lang_commands:schema_registry_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - json
        - --out
        - .artifacts/schema-registry-impl-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCHEMA-REG-001
    title: schema_registry_report_main writes report file
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
          - wrote .artifacts/schema-registry-impl-case.json
        required: true
```

## DCIMPL-PY-SCHEMA-REG-002

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
    entrypoint: spec_runner.spec_lang_commands:schema_registry_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - json
        - --check
        - --out
        - specs/07_runner_behavior/impl/python/cases/fixtures/schema_registry_report_stale.json
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-SCHEMA-REG-002
    title: schema_registry_report_main check mode fails on stale artifact
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
          - stale report artifact
        required: true
```
