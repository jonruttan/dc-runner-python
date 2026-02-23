# Python Script CLI Cases: CI and Parity

## DCIMPL-PY-SCRIPT-CI-001

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
    entrypoint: spec_runner.script_entrypoints:ci_gate_summary_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-001
    title: ci_gate_summary command help renders usage
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
          - --runner-bin
        required: true
```

## DCIMPL-PY-SCRIPT-CI-002

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
    entrypoint: spec_runner.script_entrypoints:ci_gate_summary_main
    check:
      profile: exec.command
      config:
        argv: []
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-002
    title: ci_gate_summary requires runner-bin
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
          - --runner-bin
        required: true
```

## DCIMPL-PY-SCRIPT-CI-003

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
    entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-003
    title: compare_conformance_parity command help renders usage
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

## DCIMPL-PY-SCRIPT-CI-004

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
    entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
    check:
      profile: exec.command
      config:
        argv:
        - --python-timeout-seconds
        - x
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-004
    title: compare_conformance_parity rejects invalid timeout arg
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
          - invalid int value
        required: true
```

## DCIMPL-PY-SCRIPT-CI-005

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
    entrypoint: spec_runner.script_entrypoints:python_conformance_runner_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-005
    title: python conformance runner help renders required flags
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
          - --cases
          - --out
        - std.string.contains:
          - var: stdout
          - --case-file-pattern
        required: true
```

## DCIMPL-PY-SCRIPT-CI-006

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
    entrypoint: spec_runner.script_entrypoints:python_conformance_runner_main
    check:
      profile: exec.command
      config:
        argv:
        - --cases
        - specs/conformance/cases
        - --out
        - .artifacts/python-conformance-script-case.json
        - --case-file-pattern
        - ''
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-006
    title: python conformance runner rejects empty case pattern
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

## DCIMPL-PY-SCRIPT-CI-007

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
        path: /dc-runner-php
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-007
    title: php conformance runner usage includes required flags
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
          - --cases <dir-or-file>
          - --out <file>
        - std.string.contains:
          - var: text
          - --case-file-pattern <glob>
        required: true
```

## DCIMPL-PY-SCRIPT-CI-008

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
    entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
    check:
      profile: exec.command
      config:
        argv:
        - --case-formats
        - ''
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-008
    title: compare_conformance_parity rejects empty case formats
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
          - --case-formats requires at least one format
        required: true
```

## DCIMPL-PY-SCRIPT-CI-009

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
    entrypoint: spec_runner.script_entrypoints:compare_conformance_parity_main
    env:
      PATH: /nonexistent
    check:
      profile: exec.command
      config:
        argv:
        - --cases
        - specs/conformance/cases
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-CI-009
    title: compare_conformance_parity reports missing php executable
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
          - php executable not found in PATH
        required: true
```
