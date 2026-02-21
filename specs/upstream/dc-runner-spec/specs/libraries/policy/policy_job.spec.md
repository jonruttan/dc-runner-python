```yaml contract-spec
id: LIB-POLICY-JOB-001
type: contract.export
title: reusable contract.job assertions
contract:
  defaults:
    class: MUST
  steps:
  - id: __export__policy.job.dispatch_ok
    assert:
      std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
  - id: __export__policy.job.written_path_contains
    assert:
      std.string.contains:
      - std.object.get:
        - {var: summary_json}
        - written_path
      - {var: expected_path}
  - id: __export__policy.job.hooks_present
    assert:
      std.logic.and:
      - std.object.has_key:
        - {var: job_map}
        - on_fail
      - std.object.has_key:
        - {var: job_map}
        - on_complete
harness:
  exports:
  - as: policy.job.dispatch_ok
    from: assert.function
    path: /__export__policy.job.dispatch_ok
    params: [summary_json]
    required: true
  - as: policy.job.written_path_contains
    from: assert.function
    path: /__export__policy.job.written_path_contains
    params: [summary_json, expected_path]
    required: true
  - as: policy.job.hooks_present
    from: assert.function
    path: /__export__policy.job.hooks_present
    params: [job_map]
    required: true
library:
  id: policy.job
  module: policy
  stability: alpha
  owner: dc-runner-spec
  tags: [policy, job]
```


```yaml contract-spec
id: LIB-POLICY-JOB-900
type: contract.check
title: job policy library smoke
harness:
  check:
    profile: text.file
    config: {}
  use:
  - ref: '#LIB-POLICY-JOB-001'
    as: lib_policy_job
    symbols:
    - policy.job.dispatch_ok
    - policy.job.written_path_contains
    - policy.job.hooks_present
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names: [text]
  steps:
  - id: assert_1
    assert:
    - call:
      - {var: policy.job.dispatch_ok}
      - lit: {ok: true}
    - std.logic.not:
      - call:
        - {var: policy.job.dispatch_ok}
        - lit: {ok: false}
    - call:
      - {var: policy.job.written_path_contains}
      - lit: {written_path: .artifacts/example.json}
      - .artifacts/example.json
    - std.logic.not:
      - call:
        - {var: policy.job.written_path_contains}
        - lit: {written_path: .artifacts/example.json}
        - .artifacts/other.json
    - call:
      - {var: policy.job.hooks_present}
      - lit:
          on_fail: {}
          on_complete: {}
    - std.logic.not:
      - call:
        - {var: policy.job.hooks_present}
        - lit:
            on_fail: {}
```
