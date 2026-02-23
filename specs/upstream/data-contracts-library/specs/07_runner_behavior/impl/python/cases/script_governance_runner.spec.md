# Python Script CLI Cases: Governance Runner

## DCIMPL-PY-SCRIPT-GOV-001

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
    entrypoint: spec_runner.governance_runner:run_governance_specs_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-GOV-001
    title: governance runner help renders usage
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
          - --check-prefix
        required: true
```

## DCIMPL-PY-SCRIPT-GOV-002

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
    entrypoint: spec_runner.governance_runner:run_governance_specs_main
    check:
      profile: exec.command
      config:
        argv:
        - --cases
        - specs/governance/cases
        - --case-file-pattern
        - ''
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-GOV-002
    title: governance runner rejects empty case pattern
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
          - case-file-pattern
        required: true
```

## DCIMPL-PY-SCRIPT-GOV-003

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
    entrypoint: spec_runner.governance_runner:run_governance_specs_main
    check:
      profile: exec.command
      config:
        argv:
        - --cases
        - specs/governance/cases
        - --check-prefix
        - zz.nonexistent.prefix
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-GOV-003
    title: governance runner rejects check prefix that selects no cases
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
          - selected zero cases
        required: true
```

## DCIMPL-PY-SCRIPT-GOV-004

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
        path: /dc-runner-python
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-GOV-004
    title: governance runtime registers required docgen quality checks
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
          - docs.stdlib_symbol_docs_complete
          - docs.stdlib_examples_complete
        - call:
          - var: policy.text.contains_pair
          - var: text
          - docs.harness_reference_semantics_complete
          - docs.runner_reference_semantics_complete
        - call:
          - var: policy.text.contains_pair
          - var: text
          - docs.reference_namespace_chapters_sync
          - docs.docgen_quality_score_threshold
        required: true
```
