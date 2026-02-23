```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-IMPLICIT-ID-001
    title: omitted docs id remains valid metadata
    docs:
    - summary: contract docs id intentionally omitted
      audience: spec-authors
      status: active
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
  docs:
  - summary: harness docs owner id omitted
    audience: spec-authors
    status: active
    owners:
    - role: owner
contracts:
  clauses:
  - id: DCCONF-IMPLICIT-ID-002
    title: omitted docs owner id remains valid metadata
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-IMPLICIT-ID-003
    title: missing predicate id is schema failure
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      checks:
      - assert:
          lit: true
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-IMPLICIT-ID-004
    title: synthetic report label is invalid as reference identity
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.default.4
        import: pipe_identity
      rows:
      - id: bind.invalid.synthetic
        outputs:
        - to: out_json
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.system
  defaults:
    direction: bidirectional
    imports:
    - names:
      - pipe_identity
    profile: exec.command
  actions:
  - id: svc.default.4
services:
- id: svc.default.4
  consumes:
  - svc.default.4
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.default.4
      adapter_import: pipe_identity
artifacts:
- id: out_json
  ref: artifact://implicit_ids/out_json
  type: application/json
```
