# Python Script CLI Cases: Quality and Registry Reports

## DCIMPL-PY-SCRIPT-QUALITY-001

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
    entrypoint: spec_runner.script_entrypoints:objective_scorecard_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --out
        - .artifacts/objective-scorecard-script-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-001
    title: objective_scorecard_report writes json artifact
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
          - wrote .artifacts/objective-scorecard-script-case.json
        required: true
```

## DCIMPL-PY-SCRIPT-QUALITY-002

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
    entrypoint: spec_runner.script_entrypoints:objective_scorecard_report_main
    check:
      profile: exec.command
      config:
        argv:
        - --format
        - bad
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-002
    title: objective_scorecard_report rejects invalid format
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

## DCIMPL-PY-SCRIPT-QUALITY-003

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
    entrypoint: spec_runner.script_entrypoints:quality_metric_reports_main
    check:
      profile: exec.command
      config:
        argv:
        - spec-lang-adoption
        - --out
        - .artifacts/spec-lang-adoption-script-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-003
    title: quality metric report fanout writes json artifact
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
          - wrote .artifacts/spec-lang-adoption-script-case.json
        required: true
```

## DCIMPL-PY-SCRIPT-QUALITY-004

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
    entrypoint: spec_runner.script_entrypoints:quality_metric_reports_main
    check:
      profile: exec.command
      config:
        argv:
        - nope
        - --out
        - .artifacts/quality-script-case.json
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-004
    title: quality metric report fanout rejects unknown report key
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
          - unsupported quality report
        required: true
```

## DCIMPL-PY-SCRIPT-QUALITY-005

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
        - .artifacts/schema-registry-script-case.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-005
    title: schema registry report writes json artifact
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
          - wrote .artifacts/schema-registry-script-case.json
        required: true
```

## DCIMPL-PY-SCRIPT-QUALITY-006

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
        - nope
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-QUALITY-006
    title: schema registry report rejects invalid format
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
