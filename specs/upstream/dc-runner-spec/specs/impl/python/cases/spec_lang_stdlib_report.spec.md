```yaml contract-spec
id: DCIMPL-PY-STDLIB-REP-001
title: spec_lang_stdlib_report_main emits json by default
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
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
    - call:
      - {var: policy.text.contains_pair}
      - {var: stdout}
      - '"version": 1'
      - '"summary"'
```


```yaml contract-spec
id: DCIMPL-PY-STDLIB-REP-002
title: spec_lang_stdlib_report_main emits markdown with format md
type: contract.check
harness:
  use:
  - ref: /specs/05_libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
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
    - call:
      - {var: policy.text.contains_pair}
      - {var: stdout}
      - '# Spec-Lang Stdlib Profile Report'
      - '- profile symbols:'
```
