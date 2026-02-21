```yaml contract-spec
id: DCCONF-RSTAT-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner status report schema is declared
purpose: Ensures the producer-facing status report schema exists.
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
    - std.string.contains:
      - {var: text}
      - runtime.runner_status_report
    - std.string.contains:
      - {var: text}
      - command_results
```


```yaml contract-spec
id: DCCONF-RSTAT-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: runner status matrix schema is declared
purpose: Ensures the aggregate status matrix schema exists.
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
    - std.string.contains:
      - {var: text}
      - runtime.runner_status_matrix
    - std.string.contains:
      - {var: text}
      - freshness_state
```


```yaml contract-spec
id: DCCONF-RSTAT-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ingest script enforces freshness threshold
purpose: Ensures ingest includes max-age controls and enforcement flag.
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
    - std.string.contains:
      - {var: text}
      - --max-age-hours
    - std.string.contains:
      - {var: text}
      - --enforce-freshness
```


```yaml contract-spec
id: DCCONF-RSTAT-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ingest tracks missing compatibility status visibility
purpose: Ensures missing compatibility status is represented and policy-scored.
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
    - std.string.contains:
      - {var: text}
      - freshness_state
    - std.string.contains:
      - {var: text}
      - non_blocking_fail
```


```yaml contract-spec
id: DCCONF-RSTAT-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: required lane policy remains blocking
purpose: Ensures required lane status maps to blocking policy effect.
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
    - std.string.contains:
      - {var: text}
      - lane_class
    - std.string.contains:
      - {var: text}
      - blocking_fail
```

