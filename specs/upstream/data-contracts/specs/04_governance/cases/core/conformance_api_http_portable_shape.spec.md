```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    api_http:
      allowed_top_level_keys:
      - id
      - type
      - title
      - purpose
      - request
      - requests
      - assert
      - expect
      - requires
      - harness
      allowed_assert_targets:
      - status
      - headers
      - body_text
      - body_json
      - cors_json
      - steps_json
      - context_json
      required_request_fields:
      - method
      - url
    check:
      profile: governance.scan
      config:
        check: conformance.api_http_portable_shape
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
  - id: DCGOV-CONF-API-001
    title: api.http portable conformance cases use canonical shape
    purpose: Ensures api.http portable fixtures keep setup under harness and use only
      canonical behavior assertion targets.
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
        - call:
          - var: policy.assert.summary_passed
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
        - call:
          - var: policy.assert.summary_check_id
          - std.object.assoc:
            - summary_json
            - var: summary_json
            - lit: {}
          - conformance.api_http_portable_shape
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.conformance.api.http.por.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.conformance.api.http.por.1
  consumes:
  - act.gov.conformance.api.http.por.1
```
