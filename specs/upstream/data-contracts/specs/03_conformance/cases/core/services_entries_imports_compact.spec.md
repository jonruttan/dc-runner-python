```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-027
    title: service imports compact single-name list is accepted via alias grammar
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.1
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.1
  consumes:
  - svc.check.compact.1
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.1
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-032
    title: clause imports bare-string short alias is accepted
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        service: svc.check.compact.6
    asserts:
      imports:
      - from: service
        service: svc.check.compact.6
        names:
        - pipe_identity
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.6
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.6
  consumes:
  - svc.check.compact.6
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.6
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-033
    title: predicate imports bare-string short alias is accepted
    expect:
      portable:
        status: pass
        category:
    bindings:
      defaults:
        service: svc.check.compact.7
    asserts:
      checks:
      - id: assert_1
        imports:
        - from: service
          service: svc.check.compact.7
          names:
          - pipe_identity
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.7
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.7
  consumes:
  - svc.check.compact.7
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.7
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-034
    title: clause short alias without bindings defaults service is rejected
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      imports:
      - from: service
        service:
        names:
        - pipe_identity
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.8
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.8
  consumes:
  - svc.check.compact.8
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.8
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-035
    title: clause short alias with unknown default service is rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.check.missing
    asserts:
      imports:
      - from: service
        service: svc.check.missing
        names:
        - pipe_identity
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.9
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.9
  consumes:
  - svc.check.compact.9
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.9
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-036
    title: clause short alias unknown import name is rejected
    expect:
      portable:
        status: fail
        category: schema
    bindings:
      defaults:
        service: svc.check.compact.10
    asserts:
      imports:
      - from: service
        service: svc.check.compact.10
        names:
        - unknown_import
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.10
    imports:
    - names:
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.10
  consumes:
  - svc.check.compact.10
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.10
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-028
    title: service imports compact multi-name list is accepted via alias grammar
    expect:
      portable:
        status: pass
        category:
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.2
    imports:
    - names:
      - pipe_identity
      - assert_truth
    direction: input
    profile: read.text
services:
- id: svc.check.compact.2
  consumes:
  - svc.check.compact.2
  exposes:
  - names:
    - pipe_identity
    - assert_truth
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.2
      adapter_import: pipe_identity
    assert_truth:
      adapter_action: svc.check.compact.2
      adapter_import: assert_truth
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-029
    title: service imports mixed compact and mapping item kinds are rejected
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.3
    imports:
    - names:
      - assert_truth
    direction: input
    profile: read.text
services:
- id: svc.check.compact.3
  consumes:
  - svc.check.compact.3
  exposes:
  - names:
    - assert_truth
  bindings:
    assert_truth:
      adapter_action: svc.check.compact.3
      adapter_import: assert_truth
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-030
    title: service imports compact duplicate names are rejected
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.4
    imports:
    - names:
      - pipe_identity
      - pipe_identity
    direction: input
    profile: read.text
services:
- id: svc.check.compact.4
  consumes:
  - svc.check.compact.4
  exposes:
  - names:
    - pipe_identity
  bindings:
    pipe_identity:
      adapter_action: svc.check.compact.4
      adapter_import: pipe_identity
```

```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-SCHEMA-CASE-031
    title: service imports compact unknown catalog name is rejected
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
adapters:
- type: io.fs
  actions:
  - id: svc.check.compact.5
    imports:
    - names:
      - unknown_import
    direction: input
    profile: read.text
services:
- id: svc.check.compact.5
  consumes:
  - svc.check.compact.5
  exposes:
  - names:
    - unknown_import
  bindings:
    unknown_import:
      adapter_action: svc.check.compact.5
      adapter_import: unknown_import
```
