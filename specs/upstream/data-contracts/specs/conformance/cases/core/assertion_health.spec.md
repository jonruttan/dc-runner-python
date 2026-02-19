# Assertion Health Conformance Cases

These fixtures validate assertion-health behavior independent of a specific
runtime implementation.

Coverage focus:

- per-case `assert_health.mode` behavior (`warn`, `error`, `ignore`)
- canonical diagnostic codes (`AH001`-`AH005`)
- expected outcome category (`pass` vs assertion/schema failure)

## DCCONF-AH-001

```yaml contract-spec
id: DCCONF-AH-001
title: assert_health warn emits diagnostics but case still passes
purpose: Covers warn mode behavior where diagnostics are emitted but verdict remains pass.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: warn
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
      std.string.contains:
      - {var: text}
      - ''
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-AH-002

```yaml contract-spec
id: DCCONF-AH-002
title: assert_health error mode can pass for evaluate-only assertions
purpose: Confirms error mode does not fail evaluate-only assertions when no assertion-health
  diagnostics are emitted.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
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
      std.string.contains:
      - {var: text}
      - ''
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-AH-003

```yaml contract-spec
id: DCCONF-AH-003
title: invalid assert_health.mode is a schema error
purpose: Ensures unsupported assert_health modes are rejected as schema violations.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
assert_health:
  mode: nope
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
      std.string.contains:
      - {var: text}
      - contract-spec
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-AH-004

```yaml contract-spec
id: DCCONF-AH-004
title: per-case ignore override can neutralize global strict mode
purpose: Verifies local mode override can disable stricter global assertion-health settings.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: ignore
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
      std.string.contains:
      - {var: text}
      - ''
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-AH-005

```yaml contract-spec
id: DCCONF-AH-005
title: evaluate-only sibling branches remain valid under assert_health error
purpose: Confirms evaluate-only non-redundant sibling branches do not trigger AH004 under
  assert_health error mode.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MAY
    assert:
    - std.string.contains:
      - {var: text}
      - 'version: 1'
    - std.string.contains:
      - {var: text}
      - 'version: 2'
harness:
  check:
    profile: text.file
    config: {}
```

## DCCONF-AH-006

```yaml contract-spec
id: DCCONF-AH-006
title: evaluate regex portability is handled without sugar diagnostics
purpose: Confirms evaluate regex assertions are evaluated directly without sugar-level portability
  diagnostics.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
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
      std.string.regex_match:
      - {var: text}
      - '(?<=version: )1'
harness:
  check:
    profile: text.file
    config: {}
```
