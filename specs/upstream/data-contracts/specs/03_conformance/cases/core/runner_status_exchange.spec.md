```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-RSTAT-001
    title: runner status report schema is declared
    purpose: Ensures the producer-facing status report schema exists.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - runtime.runner_status_report
          - command_results
  - id: DCCONF-RSTAT-002
    title: runner status matrix schema is declared
    purpose: Ensures the aggregate status matrix schema exists.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - runtime.runner_status_matrix
          - freshness_state
  - id: DCCONF-RSTAT-003
    title: ingest script enforces freshness threshold
    purpose: Ensures ingest includes max-age controls and enforcement flag.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - "--max-age-hours"
          - "--enforce-freshness"
  - id: DCCONF-RSTAT-004
    title: ingest tracks missing compatibility status visibility
    purpose: Ensures missing compatibility status is represented and policy-scored.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - freshness_state
          - non_blocking_fail
  - id: DCCONF-RSTAT-005
    title: required lane policy remains blocking
    purpose: Ensures required lane status maps to blocking policy effect.
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_pair
          - var: text
          - lane_class
          - blocking_fail
adapters:
- type: io.fs
  actions:
  - id: svc.assert_check.text_file.1
    config:
      use:
      - as: lib_policy_text
        symbols:
        - policy.text.contains_pair
        artifact_id: art.svc.assert_check.text_file.1.use_1.1
    direction: input
    profile: read.text
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
assets:
- id: art.svc.assert_check.text_file.1.use_1.1
  ref: "/specs/05_libraries/policy/policy_text.spec.md"
```









