```yaml contract-spec
id: DCGOV-ASSERT-SYNC-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: spec-lang builtin surface remains synced across contract and runners
purpose: Ensures builtin operators documented in the spec-lang contract are implemented in
  both Python and PHP runner evaluators.
type: contract.check
harness:
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
  - ref: /specs/05_libraries/policy/policy_core.spec.md
    as: lib_policy_core_spec
    symbols:
    - policy.pass_when_no_violations
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_2
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - assert.spec_lang_builtin_surface_sync
    imports:
    - from: artifact
      names:
      - summary_json
```
