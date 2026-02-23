```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-PROFILE-001
    title: subject profile schema defines canonical envelope fields
    purpose: Ensures subject profile schema defines JSON-core envelope and deterministic
      projection constraints.
    expect:
      portable:
        status: pass
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_all
          - var: text
          - lit:
            - profile_id
            - profile_version
            - json_core_only
            - deterministic_projection
  - id: DCCONF-PROFILE-002
    title: text.file exposes context_json subject profile envelope
    purpose: Ensures text.file harness provides context_json target with profile metadata
      and JSON value payload.
    expect:
      portable:
        status: pass
    asserts:
      imports:
      - from: asset
        names:
        - context_json
      checks:
      - id: assert_1
        assert:
        - std.logic.eq:
          - std.object.get:
            - var: context_json
            - profile_id
          - text.file/v1
        - std.logic.eq:
          - std.object.get:
            - var: context_json
            - profile_version
          - 1
        - std.object.has_key:
          - var: context_json
          - value
        - std.object.has_key:
          - var: context_json
          - meta
adapters:
- type: io.fs
  defaults:
    direction: input
    profile: read.text
  actions:
  - id: svc.assert_check.text_file.1
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_all
        artifact_id: art.svc.assert_check.text_file.1.use_1.1
      source_asset_id: art.svc.assert_check.text_file.1.source.1
  - id: svc.assert_check.text_file.2
    config:
      source_asset_id: art.svc.assert_check.text_file.2.source.1
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
- id: svc.assert_check.text_file.2
  consumes:
  - svc.assert_check.text_file.2
assets:
- id: art.svc.assert_check.text_file.1.source.1
  ref: "/specs/01_schema/subject_profiles_v1.yaml"
- id: art.svc.assert_check.text_file.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
- id: art.svc.assert_check.text_file.2.source.1
  ref: "/specs/02_contracts/20_subject_profiles_v1.md"
```


