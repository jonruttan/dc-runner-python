# Spec Lang Conformance Cases

## DCCONF-EXPR-001

```yaml contract-spec
id: DCCONF-EXPR-001
title: evaluate simple predicate passes
purpose: Verifies evaluate runs a basic true predicate against the target subject.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: pass
    category: null
harness:
  check:
    profile: text.file
    config: {}
  use:
  - ref: /specs/libraries/conformance/assertion_core.spec.md
    as: lib_assertion_core_spec
    symbols:
    - conf.pass_when_text_contains
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        call:
        - var: conf.pass_when_text_contains
        - var: text
        - 'version: 1'
```

## DCCONF-EXPR-002

```yaml contract-spec
id: DCCONF-EXPR-002
title: evaluate composed boolean passes
purpose: Verifies composed boolean expressions evaluate correctly across both runner implementations.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: pass
    category: null
harness:
  check:
    profile: text.file
    config: {}
  use:
  - ref: /specs/libraries/conformance/assertion_core.spec.md
    as: lib_assertion_core_spec
    symbols:
    - conf.pass_when_text_contains
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - call:
        - {var: conf.pass_when_text_contains}
        - {var: text}
        - version
      - std.string.starts_with:
        - {var: text}
        - '#'
```

## DCCONF-EXPR-003

```yaml contract-spec
id: DCCONF-EXPR-003
title: evaluate tail recursion is stack safe
purpose: Verifies unsupported mixed literal-expression recursive forms fail deterministically
  under mapping AST hard-cut rules.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - spec_lang let binding must be [name, expr]
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        let:
        - lit:
          - - loop
            - fn:
              - - n
                - acc
              - if:
                - eq:
                  - var: n
                  - 0
                - var: acc
                - call:
                  - var: loop
                  - sub:
                    - var: n
                    - 1
                  - add:
                    - var: acc
                    - 1
        - std.logic.eq:
          - call:
            - var: loop
            - 1500
            - 0
          - 1500
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-004

```yaml contract-spec
id: DCCONF-EXPR-004
title: evaluate false predicate fails assertion
purpose: Verifies evaluate false result is categorized as assertion failure.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: fail
    category: assertion
    message_tokens:
    - op=evaluate
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.string.starts_with:
      - {var: text}
      - NOPE_PREFIX
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-005

```yaml contract-spec
id: DCCONF-EXPR-005
title: evaluate malformed form fails schema
purpose: Verifies malformed evaluate forms fail with schema classification.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - operator args must be a list
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        bad: shape
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-006

```yaml contract-spec
id: DCCONF-EXPR-006
title: evaluate unknown symbol fails schema
purpose: Verifies unknown symbols are rejected as schema violations.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - unsupported spec_lang symbol
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        unknown_symbol:
        - 1
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-007

```yaml contract-spec
id: DCCONF-EXPR-007
title: evaluate recursive literal-expression shape fails schema
purpose: Verifies unsupported recursive literal-expression authoring shape fails deterministically
  as schema.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: fail
    category: schema
    message_tokens:
    - spec_lang let binding must be [name, expr]
harness:
  spec_lang:
    max_steps: 20
  check:
    profile: text.file
    config: {}
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        let:
        - lit:
          - - loop
            - fn:
              - - n
              - if:
                - eq:
                  - var: n
                  - 0
                - true
                - call:
                  - var: loop
                  - sub:
                    - var: n
                    - 1
        - call:
          - var: loop
          - 1000
```

## DCCONF-EXPR-008

```yaml contract-spec
id: DCCONF-EXPR-008
title: evaluate contains supports explicit subject form
purpose: Verifies evaluate contains succeeds with explicit subject arguments for the same
  target subject.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.v1
expect:
  portable:
    status: pass
    category: null
harness:
  check:
    profile: text.file
    config: {}
  use:
  - ref: /specs/libraries/conformance/assertion_core.spec.md
    as: lib_assertion_core_spec
    symbols:
    - conf.pass_when_text_contains
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
    - lit:
        call:
        - var: conf.pass_when_text_contains
        - var: text
        - 'version: 1'
    - lit:
        call:
        - var: conf.pass_when_text_contains
        - var: text
        - 'version: 1'
```

## DCCONF-EXPR-009

```yaml contract-spec
id: DCCONF-EXPR-009
title: evaluate set intersection supports deep structural equality
purpose: Verifies intersection deduplicates and compares nested values structurally with stable
  left-first output.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.set.intersection:
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":2},{"k":3}]'
        - std.json.parse:
          - '[{"k":2},{"k":4},{"k":1}]'
      - std.json.parse:
        - '[{"k":1},{"k":2}]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-010

```yaml contract-spec
id: DCCONF-EXPR-010
title: evaluate set union keeps stable left-first unique ordering
purpose: Verifies union preserves first-seen ordering while removing deep-equal duplicates.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - std.set.union:
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":2},{"k":3}]'
        - std.json.parse:
          - '[{"k":2},{"k":4},{"k":1}]'
      - std.json.parse:
        - '[{"k":1},{"k":2},{"k":3},{"k":4}]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-011

```yaml contract-spec
id: DCCONF-EXPR-011
title: evaluate difference and symmetric_difference are deterministic
purpose: Verifies set difference semantics and deterministic ordering for symmetric_difference.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.set.difference:
          - std.json.parse:
            - '[{"k":1},{"k":2},{"k":3}]'
          - std.json.parse:
            - '[{"k":2},{"k":4}]'
        - std.json.parse:
          - '[{"k":1},{"k":3}]'
      - std.logic.eq:
        - std.set.symmetric_difference:
          - std.json.parse:
            - '[{"k":1},{"k":2},{"k":3}]'
          - std.json.parse:
            - '[{"k":2},{"k":4}]'
        - std.json.parse:
          - '[{"k":1},{"k":3},{"k":4}]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-012

```yaml contract-spec
id: DCCONF-EXPR-012
title: evaluate set predicates compare by deep equality
purpose: Verifies set_equals, is_subset, is_superset, and includes use deep structural equality.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.set.set_equals:
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":3}]'
        - std.json.parse:
          - '[{"k":3},{"k":1},{"k":2}]'
      - std.set.is_subset:
        - std.json.parse:
          - '[{"k":1},{"k":2}]'
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":3}]'
      - std.set.is_superset:
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":3}]'
        - std.json.parse:
          - '[{"k":1},{"k":3}]'
      - std.collection.includes:
        - std.json.parse:
          - '[{"k":1},{"k":2},{"k":3}]'
        - std.json.parse:
          - '{"k":2}'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-013

```yaml contract-spec
id: DCCONF-EXPR-013
title: evaluate map and filter support curried builtins
purpose: Verifies builtin partial application works with map/filter collection transforms.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.collection.map:
          - call:
            - {var: std.math.add}
            - 10
          - std.json.parse:
            - '[1,2,3]'
        - std.json.parse:
          - '[11,12,13]'
      - std.logic.eq:
        - std.collection.filter:
          - call:
            - {var: std.logic.lt}
            - 3
          - std.json.parse:
            - '[1,2,3,4,5]'
        - std.json.parse:
          - '[4,5]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-014

```yaml contract-spec
id: DCCONF-EXPR-014
title: evaluate reduce and collection helpers are deterministic
purpose: Verifies reduce, reject, find, partition, group_by, and uniq_by behavior with curried
  predicates.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.collection.reduce:
          - {var: std.math.add}
          - 0
          - std.json.parse:
            - '[1,2,3,4]'
        - 10
      - std.logic.eq:
        - std.collection.reject:
          - call:
            - {var: std.logic.lt}
            - 2
          - std.json.parse:
            - '[1,2,3,4]'
        - std.json.parse:
          - '[1,2]'
      - std.logic.eq:
        - std.collection.find:
          - call:
            - {var: std.logic.lt}
            - 3
          - std.json.parse:
            - '[1,2,3,4]'
        - 4
      - std.logic.eq:
        - std.collection.partition:
          - call:
            - {var: std.logic.lt}
            - 2
          - std.json.parse:
            - '[1,2,3,4]'
        - std.json.parse:
          - '[[3,4],[1,2]]'
      - std.logic.eq:
        - std.collection.group_by:
          - fn:
            - [x]
            - if:
              - std.logic.gt:
                - {var: x}
                - 2
              - hi
              - lo
          - std.json.parse:
            - '[1,2,3,4]'
        - std.json.parse:
          - '{"lo":[1,2],"hi":[3,4]}'
      - std.logic.eq:
        - std.collection.uniq_by:
          - fn:
            - [x]
            - std.object.get:
              - {var: x}
              - k
          - std.json.parse:
            - '[{"k":1},{"k":1},{"k":2}]'
        - std.json.parse:
          - '[{"k":1},{"k":2}]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-015

```yaml contract-spec
id: DCCONF-EXPR-015
title: evaluate flatten and list composition helpers
purpose: Verifies flatten, concat, append, prepend, take, and drop operations.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.collection.flatten:
          - std.json.parse:
            - '[1,[2,[3],[]],4]'
        - std.json.parse:
          - '[1,2,3,4]'
      - std.logic.eq:
        - std.collection.concat:
          - std.json.parse:
            - '[1,2]'
          - std.json.parse:
            - '[3]'
        - std.json.parse:
          - '[1,2,3]'
      - std.logic.eq:
        - std.collection.append:
          - 3
          - std.json.parse:
            - '[1,2]'
        - std.json.parse:
          - '[1,2,3]'
      - std.logic.eq:
        - std.collection.prepend:
          - 0
          - std.json.parse:
            - '[1,2]'
        - std.json.parse:
          - '[0,1,2]'
      - std.logic.eq:
        - std.collection.take:
          - 2
          - std.json.parse:
            - '[1,2,3]'
        - std.json.parse:
          - '[1,2]'
      - std.logic.eq:
        - std.collection.drop:
          - 2
          - std.json.parse:
            - '[1,2,3]'
        - std.json.parse:
          - '[3]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-016

```yaml contract-spec
id: DCCONF-EXPR-016
title: evaluate currying chain with nested call succeeds
purpose: Verifies repeated partial application resolves deterministically to a final non-callable
  value.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - call:
        - call:
          - {var: std.math.add}
          - 2
        - 3
      - 5
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-017

```yaml contract-spec
id: DCCONF-EXPR-017
title: evaluate over-application of non-callable result is schema failure
purpose: Verifies deterministic schema failure when extra call arguments remain after returning
  non-callable value.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: fail
      category: schema
      message_tokens:
      - over-application error
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      lit:
        call:
        - call:
          - var: std.math.add
          - 1
        - 2
        - 3
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-018

```yaml contract-spec
id: DCCONF-EXPR-018
title: evaluate set ops enforce list inputs
purpose: Verifies set algebra operators reject non-list inputs with schema errors.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: fail
      category: schema
      message_tokens:
      - expects list
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.set.intersection:
      - not-a-list
      - std.json.parse:
        - '[]'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-019

```yaml contract-spec
id: DCCONF-EXPR-019
title: evaluate ramda v1 arithmetic and list utilities behave deterministically
purpose: Verifies expanded numeric and list utility forms remain pure, strict-typed, and deterministic.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.math.mul:
          - 3
          - 4
        - 12
      - std.logic.eq:
        - std.math.div:
          - 9
          - 2
        - 4.5
      - std.logic.eq:
        - std.math.mod:
          - 9
          - 4
        - 1
      - std.logic.eq:
        - std.math.pow:
          - 2
          - 5
        - 32
      - std.logic.eq:
        - std.math.clamp:
          - 1
          - 5
          - 9
        - 5
      - std.logic.eq:
        - std.math.round:
          - 2.5
        - 3
      - std.logic.eq:
        - std.collection.slice:
          - 1
          - 3
          - std.json.parse:
            - '[0,1,2,3]'
        - std.json.parse:
          - '[1,2]'
      - std.logic.eq:
        - std.collection.reverse:
          - std.json.parse:
            - '[1,2,3]'
        - std.json.parse:
          - '[3,2,1]'
      - std.logic.eq:
        - std.collection.zip:
          - std.json.parse:
            - '[1,2,3]'
          - std.json.parse:
            - '[4,5]'
        - std.json.parse:
          - '[[1,4],[2,5]]'
      - std.logic.eq:
        - std.collection.zip_with:
          - {var: std.math.add}
          - std.json.parse:
            - '[1,2,3]'
          - std.json.parse:
            - '[4,5,6]'
        - std.json.parse:
          - '[5,7,9]'
      - std.logic.eq:
        - std.math.range:
          - 2
          - 5
        - std.json.parse:
          - '[2,3,4]'
      - std.logic.eq:
        - std.collection.repeat:
          - x
          - 3
        - std.json.parse:
          - '["x","x","x"]'
      - std.type.is_null:
        - null
      - std.type.is_bool:
        - true
      - std.type.is_number:
        - 3.14
      - std.type.is_string:
        - x
      - std.type.is_list:
        - std.json.parse:
          - '[1,2]'
      - std.type.is_dict:
        - std.json.parse:
          - '{"a":1}'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-020

```yaml contract-spec
id: DCCONF-EXPR-020
title: evaluate ramda v1 object utilities
purpose: Verifies expanded object helpers keep deterministic dictionary semantics.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.object.keys:
          - std.json.parse:
            - '{"a":1,"b":2}'
        - std.json.parse:
          - '["a","b"]'
      - std.logic.eq:
        - std.object.values:
          - std.json.parse:
            - '{"a":1,"b":2}'
        - std.json.parse:
          - '[1,2]'
      - std.logic.eq:
        - std.object.entries:
          - std.json.parse:
            - '{"a":1}'
        - std.json.parse:
          - '[["a",1]]'
      - std.logic.eq:
        - std.object.merge:
          - std.json.parse:
            - '{"a":1}'
          - std.json.parse:
            - '{"b":2}'
        - std.json.parse:
          - '{"a":1,"b":2}'
      - std.logic.eq:
        - std.object.assoc:
          - b
          - 2
          - std.json.parse:
            - '{"a":1}'
        - std.json.parse:
          - '{"a":1,"b":2}'
      - std.logic.eq:
        - std.object.dissoc:
          - a
          - std.json.parse:
            - '{"a":1,"b":2}'
        - std.json.parse:
          - '{"b":2}'
      - std.logic.eq:
        - std.object.pick:
          - std.json.parse:
            - '["a"]'
          - std.json.parse:
            - '{"a":1,"b":2}'
        - std.json.parse:
          - '{"a":1}'
      - std.logic.eq:
        - std.object.omit:
          - std.json.parse:
            - '["a"]'
          - std.json.parse:
            - '{"a":1,"b":2}'
        - std.json.parse:
          - '{"b":2}'
      - std.object.prop_eq:
        - a
        - 1
        - std.json.parse:
          - '{"a":1}'
      - std.object.where:
        - std.json.parse:
          - '{"a":1}'
        - std.json.parse:
          - '{"a":1,"b":2}'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-021

```yaml contract-spec
id: DCCONF-EXPR-021
title: evaluate ramda v1 combinators and string helpers
purpose: Verifies compose/pipe, constant-function behavior, and string transforms are deterministic.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.fn.compose:
          - call:
            - {var: std.math.add}
            - 1
          - call:
            - {var: std.math.mul}
            - 2
          - 3
        - 7
      - std.logic.eq:
        - std.fn.pipe:
          - call:
            - {var: std.math.mul}
            - 2
          - call:
            - {var: std.math.add}
            - 1
          - 3
        - 7
      - std.logic.eq:
        - call:
          - call:
            - {var: std.fn.always}
            - k
          - 999
        - k
      - std.logic.eq:
        - std.string.replace:
          - a-b-c
          - '-'
          - ':'
        - a:b:c
      - std.logic.eq:
        - std.string.pad_left:
          - '7'
          - 3
          - '0'
        - '007'
      - std.logic.eq:
        - std.string.pad_right:
          - '7'
          - 3
          - '0'
        - '700'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-022

```yaml contract-spec
id: DCCONF-EXPR-022
title: evaluate ramda v1 unary numeric and compare helpers
purpose: Verifies unary numeric helpers and comparison helpers produce deterministic values
  for policy expressions.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.math.abs:
          - -7
        - 7
      - std.logic.eq:
        - std.math.negate:
          - 3
        - -3
      - std.logic.eq:
        - std.math.inc:
          - 3
        - 4
      - std.logic.eq:
        - std.math.dec:
          - 3
        - 2
      - std.logic.eq:
        - std.math.floor:
          - 3.9
        - 3
      - std.logic.eq:
        - std.math.ceil:
          - 3.1
        - 4
      - std.logic.eq:
        - std.logic.compare:
          - 3
          - 5
        - -1
      - std.logic.eq:
        - std.logic.compare:
          - 5
          - 5
        - 0
      - std.logic.eq:
        - std.logic.compare:
          - 7
          - 5
        - 1
      - std.logic.between:
        - 1
        - 3
        - 2
      - std.logic.xor:
        - true
        - false
      - std.logic.not:
        - std.logic.xor:
          - true
          - true
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-023

```yaml contract-spec
id: DCCONF-EXPR-023
title: evaluate ramda v1 utility and predicate helpers
purpose: Verifies utility and predicate helpers used by governance logic are deterministic
  and pure.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: pass
      category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.and:
      - std.logic.eq:
        - std.collection.count:
          - std.json.parse:
            - '[1,2,3]'
        - 3
      - std.logic.eq:
        - std.collection.first:
          - std.json.parse:
            - '[9,8,7]'
        - 9
      - std.logic.eq:
        - std.collection.rest:
          - std.json.parse:
            - '[9,8,7]'
        - std.json.parse:
          - '[8,7]'
      - std.logic.eq:
        - std.string.trim:
          - '  x  '
        - x
      - std.logic.eq:
        - std.string.lower:
          - AbC
        - abc
      - std.logic.eq:
        - std.string.upper:
          - AbC
        - ABC
      - std.logic.eq:
        - std.string.split:
          - a,b,c
          - ','
        - std.json.parse:
          - '["a","b","c"]'
      - std.logic.eq:
        - std.string.join:
          - std.json.parse:
            - '["a","b","c"]'
          - '-'
        - a-b-c
      - std.logic.eq:
        - std.null.coalesce:
          - null
          - x
        - x
      - std.logic.eq:
        - std.collection.distinct:
          - std.json.parse:
            - '[1,1,2,2,3]'
        - std.json.parse:
          - '[1,2,3]'
      - std.logic.eq:
        - std.collection.sort_by:
          - std.json.parse:
            - '[3,1,2]'
          - {var: std.fn.identity}
        - std.json.parse:
          - '[1,2,3]'
      - std.logic.eq:
        - std.object.pluck:
          - std.json.parse:
            - '[{"k":1},{"k":2}]'
          - k
        - std.json.parse:
          - '[1,2]'
      - std.collection.all:
        - std.json.parse:
          - '[true,true,true]'
      - std.collection.any:
        - std.json.parse:
          - '[false,true,false]'
      - std.collection.none:
        - std.json.parse:
          - '[false,false]'
      - std.collection.is_empty:
        - std.json.parse:
          - '[]'
      - std.string.matches:
        - a42
        - a[0-9]+
      - std.string.matches_all:
        - a42
        - std.json.parse:
          - '["^a","[0-9]+$"]'
      - std.string.regex_match:
        - a42
        - a[0-9]+
      - std.logic.eq:
        - std.type.json_type:
          - std.json.parse:
            - '[1,2]'
          - list
        - true
      - std.logic.eq:
        - std.type.json_type:
          - std.json.parse:
            - '{"x":1}'
          - object
        - true
      - std.logic.eq:
        - std.type.json_type:
          - std.json.parse:
            - '[1,2]'
          - array
        - true
      - std.logic.eq:
        - std.type.json_type:
          - true
          - boolean
        - true
      - std.object.has_key:
        - std.json.parse:
          - '{"x":1}'
        - x
      - std.collection.in:
        - x
        - std.json.parse:
          - '{"x":1}'
      - std.logic.eq:
        - std.collection.len:
          - abcd
        - 4
      - std.type.is_boolean:
        - true
      - std.type.is_array:
        - std.json.parse:
          - '[1,2]'
      - std.type.is_object:
        - std.json.parse:
          - '{"x":1}'
      - std.logic.eq:
        - std.math.sum:
          - std.json.parse:
            - '[1,2,3]'
        - 6
      - std.logic.eq:
        - std.math.min:
          - std.json.parse:
            - '[4,2,8]'
        - 2
      - std.logic.eq:
        - std.math.max:
          - std.json.parse:
            - '[4,2,8]'
        - 8
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-EXPR-024

```yaml contract-spec
id: DCCONF-EXPR-024
title: evaluate ramda v1 schema failures are deterministic
purpose: Verifies representative arity and type failures stay in schema category for the expanded
  builtin surface.
type: contract.check
requires:
  capabilities:
  - evaluate.spec_lang.ramda.v1
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    python:
      status: fail
      category: schema
      message_tokens:
      - arity error
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.logic.compare:
      - 1
harness:
  check:
    profile: text.file
    config: {}
```
