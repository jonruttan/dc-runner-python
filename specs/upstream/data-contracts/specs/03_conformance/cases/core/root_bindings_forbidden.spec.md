```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
bindings:
- id: bind.root.invalid
  service: svc.default.1
  import: pipe_identity
  outputs:
  - to: status
contracts:
  clauses:
  - id: DCCONF-BIND-ROOT-001
    title: contract scoped bindings schema validation
    expect:
      portable:
        status: fail
        category: schema
    asserts:
      checks:
      - id: assert_1
        assert:
          lit: true
artifacts:
- id: status
  ref: artifact://root_bindings_forbidden/status
```
