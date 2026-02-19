# Python Script CLI Cases: Governance Runner

## DCIMPL-PY-SCRIPT-GOV-001

```yaml contract-spec
id: DCIMPL-PY-SCRIPT-GOV-001
title: governance runner help renders usage
type: contract.check
harness:
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
    - std.string.contains:
      - {var: text}
      - docs.stdlib_symbol_docs_complete
    - std.string.contains:
      - {var: text}
      - docs.stdlib_examples_complete
    - std.string.contains:
      - {var: text}
      - docs.harness_reference_semantics_complete
    - std.string.contains:
      - {var: text}
      - docs.runner_reference_semantics_complete
    - std.string.contains:
      - {var: text}
      - docs.reference_namespace_chapters_sync
    - std.string.contains:
      - {var: text}
      - docs.docgen_quality_score_threshold
```
