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
        check: runtime.api_http_cors_support
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
  - id: DCGOV-RUNTIME-APIHTTP-006
    title: api.http CORS support surfaces remain synchronized
    purpose: Ensures CORS preflight and normalized cors_json projection are documented
      and implemented.
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
          - runtime.api_http_cors_support
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.runtime.api.http.cors.su.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.runtime.api.http.cors.su.1
  consumes:
  - act.gov.runtime.api.http.cors.su.1
```
