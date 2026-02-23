# Python Spec-Lang Stdlib Report Command Cases

## DCIMPL-PY-STDLIB-REP-001

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
    entrypoint: spec_runner.spec_lang_commands:spec_lang_stdlib_report_main
    check:
      profile: exec.command
      config:
        argv: []
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-STDLIB-REP-001
    title: spec_lang_stdlib_report_main emits json by default
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
        required: true
```

## DCIMPL-PY-STDLIB-REP-002

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
    entrypoint: spec_runner.spec_lang_commands:spec_lang_stdlib_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - md
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-STDLIB-REP-002
    title: spec_lang_stdlib_report_main emits markdown with format md
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
          - '# Spec-Lang Stdlib Profile Report'
          - '- profile symbols:'
        required: true
```
