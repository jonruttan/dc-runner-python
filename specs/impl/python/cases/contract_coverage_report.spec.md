# Python Contract Coverage Report Command Cases

## DCIMPL-PY-CONTRACT-REP-001

```yaml contract-spec
id: DCIMPL-PY-CONTRACT-REP-001
title: contract_coverage_report_main emits json payload to stdout
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:contract_coverage_report_main
  check:
    profile: cli.run
    config:
      argv: []
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
    - std.string.contains:
      - {var: stdout}
      - '"version": 1'
    - std.string.contains:
      - {var: stdout}
      - '"summary"'
    - std.string.contains:
      - {var: stdout}
      - '"rules"'
```

## DCIMPL-PY-CONTRACT-REP-002

```yaml contract-spec
id: DCIMPL-PY-CONTRACT-REP-002
title: contract_coverage_report_main writes output file with --out
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:contract_coverage_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --out
      - .artifacts/contract-coverage-impl-case.json
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
      - wrote .artifacts/contract-coverage-impl-case.json
```
