```yaml contract-spec
id: DCCONF-RCERT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner certification core checks MUST assertions deterministically
purpose: Confirms required certification core clauses remain strict and deterministic.
type: contract.check
harness:
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
      std.string.contains:
      - {var: text}
      - contract-spec
```


```yaml contract-spec
id: DCCONF-RCERT-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner certification core MAY assertions remain available
purpose: Ensures MAY clauses remain supported for compatibility-oriented certification checks.
type: contract.check
harness:
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
    class: MAY
    assert:
    - std.string.contains:
      - {var: text}
      - version
    - std.string.contains:
      - {var: text}
      - contract-spec
```
