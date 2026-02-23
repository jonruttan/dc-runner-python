```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
contracts:
  clauses:
  - id: DCGOV-PACK-002
    title: runner contract pack is complete
    purpose: Ensures runner-contract pack includes CLI and status exchange surfaces.
    harness:
      root: "."
      pack:
        path: "/specs/00_core/packs/runner_contract_pack_v1.yaml"
        required_tokens:
        - pack_id: runner_contract_pack_v1
        - "/specs/02_contracts/29_runner_cli_interface.md"
        - "/specs/02_contracts/30_build_tool_command_set.md"
        - "/specs/02_contracts/33_bundle_package_management.md"
        - "/specs/02_contracts/34_runner_implementation_spec_bundles.md"
        - "/specs/01_schema/runner_cli_contract_v1.yaml"
        - "/specs/01_schema/runner_build_tool_contract_v1.yaml"
        - "/specs/01_schema/project_bundle_lock_v1.yaml"
        - "/specs/01_schema/implementation_bundle_overlay_v1.yaml"
        - "/specs/01_schema/implementation_bundle_build_lock_v1.yaml"
        - "/specs/03_conformance/cases/runner_cli/runner_cli_required_help.spec.md"
        - "/specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_core.spec.md"
        - "/specs/03_conformance/cases/runner_build_tool/runner_build_tool_required_sync.spec.md"
        - "/specs/03_conformance/cases/runner_build_tool/runner_build_tool_bundle_asset_naming.spec.md"
        - "/specs/03_conformance/cases/runner_build_tool/runner_build_tool_impl_overlay_schema.spec.md"
        - "/specs/03_conformance/cases/runner_build_tool/runner_build_tool_project_lock_additional_role.spec.md"
      check:
        profile: governance.scan
        config:
          check: packs.runner_contract_pack_complete
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
