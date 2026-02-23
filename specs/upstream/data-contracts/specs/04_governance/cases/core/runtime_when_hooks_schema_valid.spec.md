```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    check:
      profile: governance.scan
      config:
        check: runtime.when_hooks_schema_valid
contracts:
  clauses:
  - id: DCGOV-RUNTIME-HOOKS-001
    title: when hooks schema must be valid
    purpose: Enforces when shape and hook expression list requirements.
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
  - id: act.gov.runtime.when.hooks.schem.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.when.hooks.schem.1
  consumes:
  - act.gov.runtime.when.hooks.schem.1
```
