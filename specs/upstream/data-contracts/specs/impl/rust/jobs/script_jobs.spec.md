# Rust Job Script Cases

## DCIMPL-RUST-JOB-001

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_job.spec.md
      as: lib_policy_job
      symbols:
      - policy.job.dispatch_ok
      - policy.job.written_path_contains
    spec_lang:
      capabilities:
      - ops.helper
      - ops.job
    jobs:
      main:
        mode: check
        helper: helper.governance.scan_bundle
        inputs:
          path: /specs
          patterns:
          - contract-spec
        outputs:
          summary: .artifacts/job-scan-summary.json
      on_fail:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-001.fail.json
          format: json
          report_name: DCIMPL-RUST-JOB-001.fail
      on_complete:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-001.complete.json
          format: json
          report_name: DCIMPL-RUST-JOB-001.complete
contracts:
  clauses:
  - id: DCIMPL-RUST-JOB-001
    title: governance scan bundle helper smoke
    purpose: Contract job entrypoint for Rust-native helper dispatch and scalar path#id
      job refs.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: artifact
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
        - ops.job.dispatch:
          - main
        - std.logic.neq:
          - std.object.get:
            - var: summary_json
            - scanned_files
          - null
        required: true
```

## DCIMPL-RUST-JOB-002

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_job.spec.md
      as: lib_policy_job
      symbols:
      - policy.job.dispatch_ok
      - policy.job.written_path_contains
    spec_lang:
      capabilities:
      - ops.helper
      - ops.job
    jobs:
      main:
        mode: check
        helper: helper.parity.run_conformance
        inputs:
          cases: specs/conformance/cases
          php_runner: dc-runner-php/conformance_runner.php
          out: .artifacts/conformance-parity.json
      on_fail:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-002.fail.json
          format: json
          report_name: DCIMPL-RUST-JOB-002.fail
      on_complete:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-002.complete.json
          format: json
          report_name: DCIMPL-RUST-JOB-002.complete
contracts:
  clauses:
  - id: DCIMPL-RUST-JOB-002
    title: conformance parity command via contract.job
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: artifact
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
        - ops.job.dispatch:
          - main
        - call:
          - var: policy.job.dispatch_ok
          - var: summary_json
        required: true
```

## DCIMPL-RUST-JOB-003

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    use:
    - ref: /payloads/data-contracts-library/core/specs/05_libraries/policy/policy_job.spec.md
      as: lib_policy_job
      symbols:
      - policy.job.dispatch_ok
      - policy.job.written_path_contains
    spec_lang:
      capabilities:
      - ops.helper
      - ops.job
    jobs:
      main:
        mode: warn
        helper: helper.perf.run_smoke
        inputs:
          report_out: .artifacts/perf-smoke-report.json
      on_fail:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-003.fail.json
          format: json
          report_name: DCIMPL-RUST-JOB-003.fail
      on_complete:
        helper: helper.report.emit
        mode: report
        inputs:
          out: .artifacts/job-hooks/DCIMPL-RUST-JOB-003.complete.json
          format: json
          report_name: DCIMPL-RUST-JOB-003.complete
contracts:
  clauses:
  - id: DCIMPL-RUST-JOB-003
    title: perf smoke command via contract.job
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: artifact
        names:
        - summary_json
      checks:
      - id: assert_1
        assert:
        - ops.job.dispatch:
          - main
        - call:
          - var: policy.job.dispatch_ok
          - var: summary_json
        required: true
```

## DCIMPL-RUST-JOB-004

```yaml contract-spec
id: DCIMPL-RUST-JOB-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: schema registry build via contract.job
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: build
      helper: helper.schema.registry_report
      inputs:
        format: json
        out: .artifacts/schema_registry_report.json
        check: false
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCIMPL-RUST-JOB-004.fail.json
        format: json
        report_name: DCIMPL-RUST-JOB-004.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCIMPL-RUST-JOB-004.complete.json
        format: json
        report_name: DCIMPL-RUST-JOB-004.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - var: summary_json
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```

## DCIMPL-RUST-JOB-005

```yaml contract-spec
id: DCIMPL-RUST-JOB-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: schema registry check via contract.job
type: contract.job
harness:
  spec_lang:
    capabilities:
    - ops.helper
    - ops.job
  jobs:
    main:
      mode: check
      helper: helper.schema.registry_report
      inputs:
        format: json
        out: .artifacts/schema_registry_report.json
        check: true
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCIMPL-RUST-JOB-005.fail.json
        format: json
        report_name: DCIMPL-RUST-JOB-005.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/DCIMPL-RUST-JOB-005.complete.json
        format: json
        report_name: DCIMPL-RUST-JOB-005.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_1
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - var: summary_json
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete
```
