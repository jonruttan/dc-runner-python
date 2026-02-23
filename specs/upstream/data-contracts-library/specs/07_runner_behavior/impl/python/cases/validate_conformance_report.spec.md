# Python Validate Conformance Report Command Cases

## DCIMPL-PY-VALREP-001

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
    entrypoint: spec_runner.spec_lang_commands:validate_report_main
    check:
      profile: exec.command
      config:
        argv:
        - specs/07_runner_behavior/impl/python/cases/fixtures/conformance_report_valid.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-VALREP-001
    title: validate_report_main passes for valid report payload
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
          - 'OK: valid conformance report'
        required: true
```

## DCIMPL-PY-VALREP-002

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
    entrypoint: spec_runner.spec_lang_commands:validate_report_main
    check:
      profile: exec.command
      config:
        argv:
        - specs/07_runner_behavior/impl/python/cases/fixtures/conformance_report_invalid.json
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-VALREP-002
    title: validate_report_main fails for invalid report payload
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
          - 'ERROR: report.version must equal 1'
        required: true
```
