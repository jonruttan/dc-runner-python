```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-JOB-004
    title: schema registry build via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-005
    title: schema registry check via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-006
    title: docs lint via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-007
    title: docs generate build via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-008
    title: docs generate check via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-009
    title: docs build reference book via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-010
    title: docs build check reference book via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
  - id: DCCONF-JOB-011
    title: docs graph export via contract.job
    purpose: Ensures script command contracts dispatch and return deterministic success
      state.
    when:
      fail:
      - ops.job.dispatch:
        - on_fail
      complete:
      - ops.job.dispatch:
        - on_complete
    asserts:
      imports:
      - from: asset
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
adapters:
- type: io.system
  defaults:
    direction: input
    profile: exec.command
  actions:
  - id: svc.assert_check.default.1
    config:
      jobs:
      - id: main
        mode: build
        helper: helper.schema.registry_report
        inputs:
          format: json
          out: ".artifacts/schema_registry_report.json"
          check: false
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-004.fail.json"
          format: json
          report_name: DCCONF-JOB-004.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-004.complete.json"
          format: json
          report_name: DCCONF-JOB-004.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.1.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.2
    config:
      jobs:
      - id: main
        mode: check
        helper: helper.schema.registry_report
        inputs:
          format: json
          out: ".artifacts/schema_registry_report.json"
          check: true
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-005.fail.json"
          format: json
          report_name: DCCONF-JOB-005.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-005.complete.json"
          format: json
          report_name: DCCONF-JOB-005.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.2.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.3
    config:
      jobs:
      - id: main
        mode: lint
        helper: helper.docs.lint
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-006.fail.json"
          format: json
          report_name: DCCONF-JOB-006.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-006.complete.json"
          format: json
          report_name: DCCONF-JOB-006.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.3.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.4
    config:
      jobs:
      - id: main
        mode: build
        helper: helper.docs.generate_all
        inputs:
          action: build
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-007.fail.json"
          format: json
          report_name: DCCONF-JOB-007.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-007.complete.json"
          format: json
          report_name: DCCONF-JOB-007.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.4.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.5
    config:
      jobs:
      - id: main
        mode: check
        helper: helper.docs.generate_all
        inputs:
          action: check
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-008.fail.json"
          format: json
          report_name: DCCONF-JOB-008.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-008.complete.json"
          format: json
          report_name: DCCONF-JOB-008.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.5.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.6
    config:
      jobs:
      - id: main
        mode: build
        helper: helper.docs.generate_all
        inputs:
          action: build
          surface: reference_book
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-009.fail.json"
          format: json
          report_name: DCCONF-JOB-009.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-009.complete.json"
          format: json
          report_name: DCCONF-JOB-009.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.6.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.7
    config:
      jobs:
      - id: main
        mode: check
        helper: helper.docs.generate_all
        inputs:
          action: check
          surface: reference_book
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-010.fail.json"
          format: json
          report_name: DCCONF-JOB-010.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-010.complete.json"
          format: json
          report_name: DCCONF-JOB-010.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.7.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
  - id: svc.assert_check.default.8
    config:
      jobs:
      - id: main
        mode: build
        helper: helper.docs.generate_all
        inputs:
          action: build
          surface: docs_graph
      - id: on_fail
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-011.fail.json"
          format: json
          report_name: DCCONF-JOB-011.fail
      - id: on_complete
        helper: helper.report.emit
        mode: report
        inputs:
          out: ".artifacts/job-hooks/DCCONF-JOB-011.complete.json"
          format: json
          report_name: DCCONF-JOB-011.complete
      use:
      - as: lib_policy_job
        symbols:
        - policy.job.dispatch_ok
        - policy.job.written_path_contains
        artifact_id: art.svc.assert_check.default.8.use_1.1
      spec_lang:
        capabilities:
        - ops.helper
        - ops.job
services:
- id: svc.assert_check.default.1
  consumes:
  - svc.assert_check.default.1
- id: svc.assert_check.default.2
  consumes:
  - svc.assert_check.default.2
- id: svc.assert_check.default.3
  consumes:
  - svc.assert_check.default.3
- id: svc.assert_check.default.4
  consumes:
  - svc.assert_check.default.4
- id: svc.assert_check.default.5
  consumes:
  - svc.assert_check.default.5
- id: svc.assert_check.default.6
  consumes:
  - svc.assert_check.default.6
- id: svc.assert_check.default.7
  consumes:
  - svc.assert_check.default.7
- id: svc.assert_check.default.8
  consumes:
  - svc.assert_check.default.8
assets:
- id: art.svc.assert_check.default.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.2.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.3.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.4.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.5.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.6.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.7.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
- id: art.svc.assert_check.default.8.use_1.1
  ref: "/specs/05_libraries/policy/policy_job.spec.md"
```














