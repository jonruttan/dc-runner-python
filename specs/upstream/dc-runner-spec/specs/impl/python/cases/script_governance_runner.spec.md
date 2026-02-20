# Python Script CLI Cases: Governance Runner

## DCIMPL-PY-SCRIPT-GOV-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-GOV-001
title: governance runner help renders usage
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.governance_runner:run_governance_specs_main
  check:
    profile: cli.run
    config:
      argv:
      - --help
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
      - --check-prefix
```

## DCIMPL-PY-SCRIPT-GOV-002

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-GOV-002
title: governance runner rejects empty case pattern
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.governance_runner:run_governance_specs_main
  check:
    profile: cli.run
    config:
      argv:
      - --cases
      - specs/governance/cases
      - --case-file-pattern
      - ''
      exit_code: 2
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
      - case-file-pattern
```

## DCIMPL-PY-SCRIPT-GOV-003

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-GOV-003
title: governance runner rejects check prefix that selects no cases
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  entrypoint: spec_runner.governance_runner:run_governance_specs_main
  check:
    profile: cli.run
    config:
      argv:
      - --cases
      - specs/governance/cases
      - --check-prefix
      - zz.nonexistent.prefix
      exit_code: 2
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
      - selected zero cases
```

## DCIMPL-PY-SCRIPT-GOV-004

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-GOV-004
title: governance runtime registers required docgen quality checks
type: contract.check
harness:
  use:
  - ref: /specs/libraries/policy/policy_text.spec.md
    as: lib_policy_text
    symbols:
    - policy.text.contains_pair
    - policy.text.contains_all
    - policy.text.contains_none
  check:
    profile: text.file
    config:
      path: /dc-runner-python
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
    - call:
      - {var: policy.text.contains_pair}
      - {var: text}
      - docs.stdlib_symbol_docs_complete
      - docs.stdlib_examples_complete
    - call:
      - {var: policy.text.contains_pair}
      - {var: text}
      - docs.harness_reference_semantics_complete
      - docs.runner_reference_semantics_complete
    - call:
      - {var: policy.text.contains_pair}
      - {var: text}
      - docs.reference_namespace_chapters_sync
      - docs.docgen_quality_score_threshold
```
