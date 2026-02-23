# PHP Spec Runner Library Export References

## DCIMPL-PHP-RUN-LIB-001

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /specs/05_libraries/impl/assertion_core.spec.md
      as: lib_assertion_core_spec
      symbols:
      - impl.assert.contains
      - impl.assert.json_type
      - impl.assert.regex
    check:
      profile: read.text
      config: {}
contracts:
  clauses:
  - id: DCIMPL-PHP-RUN-LIB-001
    title: impl assertion library exports are referenced by impl fixtures
    purpose: References impl assertion library exports for governance usage tracking.
    expect:
      portable:
        status: pass
        category: null
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - '# PHP Spec Runner Library Export References'
        required: true
```
