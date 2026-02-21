These fixtures pin down entrypoint resolution behavior for `type: cli.run`.

Coverage focus:

- explicit `harness.entrypoint` behavior
- capability-gated skip behavior for runtimes without `cli.run`


```yaml contract-spec
id: DCCONF-CLI-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: conformance fixture sets explicit cli.run harness.entrypoint
purpose: Defines portable behavior for explicit cli.run entrypoint when capability is present.
type: contract.check
requires:
  capabilities:
  - cli.run
  - cli.run.entrypoint_conformance
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    php:
      status: skip
      category: null
harness:
  entrypoint: spec_runner.conformance_fixtures:main
  check:
    profile: cli.run
    config:
      argv:
      - --help
      exit_code: 0
contract:
  defaults:
    class: MUST
  steps: []
```


```yaml contract-spec
id: DCCONF-CLI-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: explicit entrypoint drives cli.run behavior deterministically
purpose: Pins deterministic behavior for explicit harness entrypoint execution.
type: contract.check
requires:
  capabilities:
  - cli.run
  - cli.run.entrypoint_conformance
  when_missing: skip
expect:
  portable:
    status: skip
    category: null
  impl:
    php:
      status: skip
      category: null
harness:
  entrypoint: spec_runner.conformance_fixtures:main
  check:
    profile: cli.run
    config:
      argv:
      - --json
      exit_code: 0
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stdout
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stdout}
      - '"ok": true'
```
