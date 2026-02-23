```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
title: schema alias registry harmonization
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-ALIAS-001
    title: services imports compact aliases remain valid via alias registry
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-002
    title: clause imports support canonical and compact aliases together
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
    asserts:
      imports:
      - from: service
        service: svc.alias.harmonize.1
        names:
        - pipe_identity
      - from: service
        service: svc.alias.harmonize.1
        names:
        - assert_truth
      - from: service
        service: svc.alias.harmonize.1
        names:
        - pipe_identity
        as:
          pipe_identity: subject
      checks:
      - id: assert_1
        assert:
          std.logic.eq:
          - var: subject
          - pipe_identity
  - id: DCCONF-SCHEMA-ALIAS-003
    title: effective-required binding import missing after merge is rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        mode: merge
      rows:
      - id: bind_alias_missing_import
        outputs:
        - to: alias_output
          as: subject
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-004
    title: terminology contract for accepted preferred canonical normalized forms
      is aligned
    purpose: Captures harmonized terminology contract between alias registry and v1
      schema docs.
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-005
    title: bindings outputs compact list strings are accepted
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_compact_output
        outputs:
        - to: alias_output
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-006
    title: bindings inputs compact list strings are accepted
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_compact_input
        inputs:
        - from: alias_input
        outputs:
        - to: alias_output
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-007
    title: mixed compact and mapping output rows are rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_mixed_output
        outputs:
        - to: alias_output
        - to: alias_output
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-008
    title: empty compact output row is rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_empty_output
        outputs:
        - to: " "
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-009
    title: duplicate compact output rows are rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_duplicate_output
        outputs:
        - to: alias_output
        - to: alias_output
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
  - id: DCCONF-SCHEMA-ALIAS-010
    title: mixed compact and mapping input rows are rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.alias.harmonize.1
        import: pipe_identity
        mode: merge
      rows:
      - id: bind_alias_mixed_input
        inputs:
        - from: alias_input
        - from: alias_input
          as: alias_subject
        outputs:
        - to: alias_output
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.alias.harmonize.1
    imports:
    - names:
      - pipe_identity
      - assert_truth
    direction: input
    profile: read.text
services:
- id: svc.alias.harmonize.1
  consumes:
  - svc.alias.harmonize.1
  exposes:
  - names:
    - pipe_identity
    - assert_truth
  bindings:
    pipe_identity:
      adapter_action: svc.alias.harmonize.1
      adapter_import: pipe_identity
    assert_truth:
      adapter_action: svc.alias.harmonize.1
      adapter_import: assert_truth
assets:
- id: alias_input
  ref: "/specs/01_schema/schema_v1.md"
artifacts:
- id: alias_output
  ref: "/specs/01_schema/schema_v1.md"
```
