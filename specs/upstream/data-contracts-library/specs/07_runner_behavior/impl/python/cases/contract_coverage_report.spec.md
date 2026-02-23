# Python Contract Coverage Report Command Cases

## DCIMPL-PY-CONTRACT-REP-001

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
    entrypoint: spec_runner.spec_lang_commands:contract_coverage_report_main
    check:
      profile: exec.command
      config:
        argv: []
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-CONTRACT-REP-001
    title: contract_coverage_report_main emits json payload to stdout
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
          - '"version": 1'
          - '"summary"'
        - std.string.contains:
          - var: stdout
          - '"rules"'
        required: true
```

## DCIMPL-PY-CONTRACT-REP-002

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
    entrypoint: spec_runner.spec_lang_commands:contract_coverage_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --out
        - .artifacts/contract-coverage-impl-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-CONTRACT-REP-002
    title: contract_coverage_report_main writes output file with --out
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
          - wrote .artifacts/contract-coverage-impl-case.json
        required: true
```
