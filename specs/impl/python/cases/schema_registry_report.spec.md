# Python Schema Registry Report Command Cases

## DCIMPL-PY-SCHEMA-REG-001

```yaml contract-spec
id: DCIMPL-PY-SCHEMA-REG-001
title: schema_registry_report_main writes report file
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:schema_registry_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --format
      - json
      - --out
      - .artifacts/schema-registry-impl-case.json
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
      - wrote .artifacts/schema-registry-impl-case.json
```

## DCIMPL-PY-SCHEMA-REG-002

```yaml contract-spec
id: DCIMPL-PY-SCHEMA-REG-002
title: schema_registry_report_main check mode fails on stale artifact
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:schema_registry_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --format
      - json
      - --check
      - --out
      - specs/impl/python/fixtures/schema_registry_report_stale.json
      exit_code: 1
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
      - stale report artifact
```
