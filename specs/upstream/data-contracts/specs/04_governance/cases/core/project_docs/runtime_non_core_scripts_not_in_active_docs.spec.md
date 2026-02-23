```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-RUNTIME-CORE-002
    title: non-core scripts are absent from active docs
    purpose: Ensures docs do not direct users to retired non-core script entrypoints.
    harness:
      root: "."
      docs_paths:
      - "/README.md"
      - "/docs/development.md"
      - "/docs/book/10_getting_started.md"
      - "/docs/book/60_runner_and_gates.md"
      - "/docs/book/90_reference_guide.md"
      forbidden_tokens:
      - scripts/core_gate.sh
      - scripts/local_ci_parity.sh
      - scripts/docs_doctor.sh
      - scripts/install_git_hooks.sh
      - scripts/prepush_gate.sh
      check:
        profile: governance.scan
        config:
          check: runtime.non_core_scripts_not_in_active_docs
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
```
