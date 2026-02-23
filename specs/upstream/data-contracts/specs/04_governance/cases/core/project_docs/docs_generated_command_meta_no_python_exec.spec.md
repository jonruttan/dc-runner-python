```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    generated_command_meta:
      files:
      - /docs/book/99_generated_reference_index.md
      required_tokens:
      - ./scripts/control_plane.sh docs-generate-check
      forbidden_tokens:
      - PYTHONPATH=runners/python
      - .venv/bin/python
      - spec_runner.spec_lang_commands
    check:
      profile: governance.scan
      config:
        check: docs.generated_command_meta_no_python_exec
    use:
    - ref: /specs/05_libraries/policy/policy_assertions.spec.md
      as: lib_policy_core_spec
      symbols:
      - policy.assert.no_violations
      - policy.assert.summary_passed
      - policy.assert.summary_check_id
      - policy.assert.scan_pass
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-011
    title: generated docs command metadata avoids python execution
    purpose: Ensures generated docs `doc-meta.commands` use canonical rust adapter
      commands and do not reintroduce python execution tokens.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.generated.command.m.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.generated.command.m.1
  consumes:
  - act.gov.docs.generated.command.m.1
```
