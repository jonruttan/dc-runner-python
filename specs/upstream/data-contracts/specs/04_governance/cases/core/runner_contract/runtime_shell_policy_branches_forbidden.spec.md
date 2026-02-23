```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-RUNTIME-SHELL-001
    title: control plane shell branch integrity
    purpose: Ensures active control-plane shell entrypoints do not embed policy verdict branching text.
    harness:
      root: "."
      control_plane_shell:
        path: "/scripts/control_plane.sh"
        forbidden_tokens:
        - README missing required task path token
        - runtime runner execution references are forbidden
        - missing required file:
      check:
        profile: governance.scan
        config:
          check: runtime.shell_policy_branches_forbidden
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
