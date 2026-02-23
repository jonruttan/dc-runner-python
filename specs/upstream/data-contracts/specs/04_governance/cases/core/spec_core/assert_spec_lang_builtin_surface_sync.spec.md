```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    root: .
    spec_lang_builtin_sync:
      required_ops:
      - std.math.mul
      - std.math.div
      - std.math.mod
      - std.math.pow
      - std.math.abs
      - std.math.negate
      - std.math.inc
      - std.math.dec
      - std.math.clamp
      - std.math.round
      - std.math.floor
      - std.math.ceil
      - std.logic.compare
      - std.logic.between
      - std.logic.xor
      - std.collection.slice
      - std.collection.reverse
      - std.collection.zip
      - std.collection.zip_with
      - std.math.range
      - std.collection.repeat
      - std.object.keys
      - std.object.values
      - std.object.entries
      - std.object.merge
      - std.object.assoc
      - std.object.dissoc
      - std.object.pick
      - std.object.omit
      - std.object.prop_eq
      - std.object.where
      - std.fn.compose
      - std.fn.pipe
      - std.fn.identity
      - std.fn.always
      - std.string.replace
      - std.string.pad_left
      - std.string.pad_right
      - std.type.is_null
      - std.type.is_bool
      - std.type.is_number
      - std.type.is_string
      - std.type.is_list
      - std.type.is_dict
    check:
      profile: governance.scan
      config:
        check: assert.spec_lang_builtin_surface_sync
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
  - id: DCGOV-ASSERT-SYNC-005
    title: spec-lang builtin surface remains synced across contract and runners
    purpose: Ensures builtin operators documented in the spec-lang contract are implemented
      in both Python and PHP runner evaluators.
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
          - assert.spec_lang_builtin_surface_sync
        imports:
        - from: asset
          names:
          - summary_json
adapters:
- type: beta.scan
  actions:
  - id: act.gov.assert.spec.lang.builtin.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.assert.spec.lang.builtin.1
  consumes:
  - act.gov.assert.spec.lang.builtin.1
```
