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
        check: library.public_surface_model
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
  - id: DCGOV-LIB-SURFACE-001
    title: library public/private surface model is enforced
    purpose: Ensures spec_lang.export cases use defines.public/defines.private scopes
      and do not use canonical export shape.
    asserts:
      imports:
      - from: asset
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - library.public_surface_model
adapters:
- type: beta.scan
  actions:
  - id: act.gov.library.public.surface.m.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.library.public.surface.m.1
  consumes:
  - act.gov.library.public.surface.m.1
```
