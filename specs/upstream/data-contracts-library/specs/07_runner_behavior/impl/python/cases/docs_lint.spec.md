# Python Docs Lint Command Cases

## DCIMPL-PY-DOCSLINT-001

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
    entrypoint: spec_runner.spec_lang_commands:docs_lint_main
    check:
      profile: exec.command
      config:
        argv: []
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-DOCSLINT-001
    title: docs_lint_main passes for canonical reference manifest
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
          - 'OK: docs lint passed'
        required: true
```

## DCIMPL-PY-DOCSLINT-002

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
    entrypoint: spec_runner.spec_lang_commands:docs_lint_main
    check:
      profile: exec.command
      config:
        argv:
        - --manifest
        - specs/07_runner_behavior/impl/python/cases/fixtures/missing_reference_manifest.yaml
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-DOCSLINT-002
    title: docs_lint_main fails when manifest path is missing
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
          - missing reference manifest
        required: true
```
