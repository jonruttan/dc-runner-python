# Runner Status Exchange Conformance Cases

## DCCONF-RSTAT-001

```yaml contract-spec
id: DCCONF-RSTAT-001
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

## DCCONF-RSTAT-002

```yaml contract-spec
id: DCCONF-RSTAT-002
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

## DCCONF-RSTAT-003

```yaml contract-spec
id: DCCONF-RSTAT-003
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

## DCCONF-RSTAT-004

```yaml contract-spec
id: DCCONF-RSTAT-004
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

## DCCONF-RSTAT-005

```yaml contract-spec
id: DCCONF-RSTAT-005
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

