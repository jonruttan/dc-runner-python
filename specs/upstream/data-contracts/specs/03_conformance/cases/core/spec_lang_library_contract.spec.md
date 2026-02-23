```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-LIB-CONTRACT-001
    title: policy library uses producer harness exports
    purpose: Ensures policy library authoring uses producer-owned root exports mode=function
      with assert.function source mappings.
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
            - 'type: spec.export'
            - 'harness:'
            - 'exports:'
            - 'from: assert.function'
        - call:
          - var: policy.text.contains_none
          - var: text
          - lit:
            - 'defines:'
  - id: DCCONF-LIB-CONTRACT-002
    title: path library uses producer harness exports
    purpose: Ensures path library authoring uses producer-owned root exports mode=function
      with assert.function source mappings.
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
            - 'type: spec.export'
            - 'harness:'
            - 'exports:'
            - 'from: assert.function'
        - call:
          - var: policy.text.contains_none
          - var: text
          - lit:
            - 'defines:'
  - id: DCCONF-LIB-CONTRACT-003
    title: policy library index tracks canonical files
    purpose: Ensures generated policy library index includes canonical file references.
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
            - "/specs/05_libraries/policy/policy_core.spec.md"
            - "/specs/05_libraries/policy/policy_metrics.spec.md"
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
        - policy.text.contains_none
        artifact_id: art.svc.assert_check.text_file.1.use_1.1
      source_asset_id: art.svc.assert_check.text_file.1.source.1
  - id: svc.assert_check.text_file.2
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_all
        - policy.text.contains_none
        artifact_id: art.svc.assert_check.text_file.2.use_1.1
      source_asset_id: art.svc.assert_check.text_file.2.source.1
  - id: svc.assert_check.text_file.3
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_all
        artifact_id: art.svc.assert_check.text_file.3.use_1.1
      source_asset_id: art.svc.assert_check.text_file.3.source.1
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
- id: svc.assert_check.text_file.2
  consumes:
  - svc.assert_check.text_file.2
- id: svc.assert_check.text_file.3
  consumes:
  - svc.assert_check.text_file.3
assets:
- id: art.svc.assert_check.text_file.1.source.1
  ref: "/specs/05_libraries/policy/policy_core.spec.md"
- id: art.svc.assert_check.text_file.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
- id: art.svc.assert_check.text_file.2.source.1
  ref: "/specs/05_libraries/path/path_core.spec.md"
- id: art.svc.assert_check.text_file.2.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
- id: art.svc.assert_check.text_file.3.source.1
  ref: "/specs/05_libraries/policy/index.md"
- id: art.svc.assert_check.text_file.3.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
```



