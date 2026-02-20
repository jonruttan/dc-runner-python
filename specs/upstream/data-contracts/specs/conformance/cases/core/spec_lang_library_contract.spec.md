# Spec-Lang Library Contract Conformance Cases

## DCCONF-LIB-CONTRACT-001

```yaml contract-spec
id: DCCONF-LIB-CONTRACT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: policy library uses producer harness exports
purpose: Ensures policy library authoring uses producer-owned harness.exports with assert.function
  source mappings.
type: contract.check
expect:
  portable:
    status: pass
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
    - std.string.contains:
      - {var: text}
      - 'type: spec.export'
    - std.string.contains:
      - {var: text}
      - 'harness:'
    - std.string.contains:
      - {var: text}
      - 'exports:'
    - std.string.contains:
      - {var: text}
      - 'from: assert.function'
    - std.logic.not:
      - std.string.contains:
        - {var: text}
        - 'defines:'
harness:
  check:
    profile: text.file
    config:
      path: /specs/libraries/policy/policy_core.spec.md
```

## DCCONF-LIB-CONTRACT-002

```yaml contract-spec
id: DCCONF-LIB-CONTRACT-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: path library uses producer harness exports
purpose: Ensures path library authoring uses producer-owned harness.exports with assert.function
  source mappings.
type: contract.check
expect:
  portable:
    status: pass
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
    - std.string.contains:
      - {var: text}
      - 'type: spec.export'
    - std.string.contains:
      - {var: text}
      - 'harness:'
    - std.string.contains:
      - {var: text}
      - 'exports:'
    - std.string.contains:
      - {var: text}
      - 'from: assert.function'
    - std.logic.not:
      - std.string.contains:
        - {var: text}
        - 'defines:'
harness:
  check:
    profile: text.file
    config:
      path: /specs/libraries/path/path_core.spec.md
```

## DCCONF-LIB-CONTRACT-003

```yaml contract-spec
id: DCCONF-LIB-CONTRACT-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: policy library index tracks canonical files
purpose: Ensures generated policy library index includes canonical file references.
type: contract.check
expect:
  portable:
    status: pass
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
    - std.string.contains:
      - {var: text}
      - /specs/libraries/policy/policy_core.spec.md
    - std.string.contains:
      - {var: text}
      - /specs/libraries/policy/policy_metrics.spec.md
harness:
  check:
    profile: text.file
    config:
      path: /specs/libraries/policy/index.md
```
