# Python Spec-Lang Stdlib Report Command Cases

## DCIMPL-PY-STDLIB-REP-001

```yaml contract-spec
id: DCIMPL-PY-STDLIB-REP-001
title: spec_lang_stdlib_report_main emits json by default
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:spec_lang_stdlib_report_main
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
```

## DCIMPL-PY-STDLIB-REP-002

```yaml contract-spec
id: DCIMPL-PY-STDLIB-REP-002
title: spec_lang_stdlib_report_main emits markdown with format md
type: contract.check
harness:
  entrypoint: spec_runner.spec_lang_commands:spec_lang_stdlib_report_main
  check:
    profile: cli.run
    config:
      argv:
      - --format
      - md
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
      - '# Spec-Lang Stdlib Profile Report'
    - std.string.contains:
      - {var: stdout}
      - '- profile symbols:'
```
