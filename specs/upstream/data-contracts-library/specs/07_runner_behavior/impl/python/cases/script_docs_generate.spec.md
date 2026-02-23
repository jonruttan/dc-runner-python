# Python Script CLI Cases: Docs Generate and Style

## DCIMPL-PY-SCRIPT-DOCS-001

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
    entrypoint: spec_runner.script_entrypoints:docs_generate_all_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-001
    title: docs_generate_all help renders usage
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
          - --surface
        required: true
```

## DCIMPL-PY-SCRIPT-DOCS-002

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
    entrypoint: spec_runner.script_entrypoints:docs_generate_all_main
    check:
      profile: exec.command
      config:
        argv:
        - --check
        - --surface
        - nope
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-002
    title: docs_generate_all fails on unknown surface
    asserts:
      imports:
      - from: artifact
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
          std.logic.eq:
          - 1
          - 1
        required: true
```

## DCIMPL-PY-SCRIPT-DOCS-003

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
    entrypoint: spec_runner.script_entrypoints:docs_generate_specs_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-003
    title: docs_generate_specs help renders usage
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

## DCIMPL-PY-SCRIPT-DOCS-004

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
    entrypoint: spec_runner.script_entrypoints:docs_generate_specs_main
    check:
      profile: exec.command
      config:
        argv:
        - --check
        - --surface
        - nope
        exit_code: 1
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-004
    title: docs_generate_specs fails on unknown surface
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
          - unknown surface_id
        required: true
```

## DCIMPL-PY-SCRIPT-DOCS-005

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
    entrypoint: spec_runner.script_entrypoints:evaluate_style_main
    check:
      profile: exec.command
      config:
        argv:
        - --help
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-005
    title: evaluate_style help renders usage
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

## DCIMPL-PY-SCRIPT-DOCS-006

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
    entrypoint: spec_runner.script_entrypoints:evaluate_style_main
    check:
      profile: exec.command
      config:
        argv:
        - --check
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-006
    title: evaluate_style check defaults to docs spec tree
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
          - formatting is canonical
        required: true
```

## DCIMPL-PY-SCRIPT-DOCS-007

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
    entrypoint: spec_runner.script_entrypoints:docs_build_reference_main
    check:
      profile: exec.command
      config:
        argv:
        - --manifest
        - docs/book/reference_manifest.yaml
        - --index-out
        - .artifacts/docs-build-reference-index.md
        - --coverage-out
        - .artifacts/docs-build-reference-coverage.md
        - --graph-out
        - .artifacts/docs-build-reference-graph.json
        exit_code: 0
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-007
    title: docs_build_reference writes artifacts to explicit outputs
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
          - wrote .artifacts/docs-build-reference-index.md
          - wrote .artifacts/docs-build-reference-coverage.md
        - std.string.contains:
          - var: stdout
          - wrote .artifacts/docs-build-reference-graph.json
        required: true
```

## DCIMPL-PY-SCRIPT-DOCS-008

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
    entrypoint: spec_runner.script_entrypoints:docs_build_reference_main
    check:
      profile: exec.command
      config:
        argv:
        - --bad-flag
        exit_code: 2
contracts:
  clauses:
  - id: DCIMPL-PY-SCRIPT-DOCS-008
    title: docs_build_reference rejects unknown args
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
