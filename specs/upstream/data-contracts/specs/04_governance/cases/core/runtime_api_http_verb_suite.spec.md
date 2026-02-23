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
        check: runtime.api_http_verb_suite
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
  - id: DCGOV-RUNTIME-APIHTTP-005
    title: api.http practical verb suite remains covered and validated
    purpose: Ensures api.http fixtures cover GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS
      and reject unsupported methods.
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
      - id: assert_2
        assert:
          call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - runtime.api_http_verb_suite
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.api.http.verb.su.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.api.http.verb.su.1
  consumes:
  - act.gov.runtime.api.http.verb.su.1
```
