These fixtures pin down entrypoint resolution behavior for `type: cli.run`.

Coverage focus:

- explicit `harness.entrypoint` behavior
- capability-gated skip behavior for runtimes without `cli.run`


```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-CLI-001
    title: conformance fixture sets explicit cli.run harness.entrypoint
    purpose: Defines portable behavior for explicit cli.run entrypoint when capability is present.
    expect:
      portable:
        status: skip
        category:
      overrides:
      - runner: php
        status: skip
        category:
    asserts:
      steps: []
  - id: DCCONF-CLI-002
    title: explicit entrypoint drives cli.run behavior deterministically
    purpose: Pins deterministic behavior for explicit harness entrypoint execution.
    expect:
      portable:
        status: skip
        category:
      overrides:
      - runner: php
        status: skip
        category:
    asserts:
      imports:
      - from: asset
        names:
        - stdout
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: stdout
          - '"ok": true'
adapters:
- type: io.system
  defaults:
    direction: input
    profile: exec.command
  actions:
  - id: svc.assert_check.cli_run.1
    config:
      argv:
      - "--help"
      exit_code: 0
      entrypoint: spec_runner.conformance_fixtures:main
  - id: svc.assert_check.cli_run.2
    config:
      argv:
      - "--json"
      exit_code: 0
      entrypoint: spec_runner.conformance_fixtures:main
services:
- id: svc.assert_check.cli_run.1
  consumes:
  - svc.assert_check.cli_run.1
- id: svc.assert_check.cli_run.2
  consumes:
  - svc.assert_check.cli_run.2
```


