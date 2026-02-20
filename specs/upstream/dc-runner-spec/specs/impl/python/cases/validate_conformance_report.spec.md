# Python Validate Conformance Report Command Cases

## DCIMPL-PY-VALREP-001

```yaml contract-spec
id: DCIMPL-PY-VALREP-001
title: validate_report_main passes for valid report payload
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.spec_lang_commands:validate_report_main
  check:
    profile: cli.run
    config:
      argv:
      - specs/impl/python/cases/fixtures/conformance_report_valid.json
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
      - 'OK: valid conformance report'
```

## DCIMPL-PY-VALREP-002

```yaml contract-spec
id: DCIMPL-PY-VALREP-002
title: validate_report_main fails for invalid report payload
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.spec_lang_commands:validate_report_main
  check:
    profile: cli.run
    config:
      argv:
      - specs/impl/python/cases/fixtures/conformance_report_invalid.json
      exit_code: 1
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - stderr
  steps:
  - id: assert_1
    assert:
      std.string.contains:
      - {var: stderr}
      - 'ERROR: report.version must equal 1'
```
