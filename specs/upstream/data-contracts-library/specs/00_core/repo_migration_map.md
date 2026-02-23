# Repo Migration Map

This map records hard-cut migration into `data-contracts-library`.

## Repository Migrations

| Source Repository | Status | Destination Root |
|---|---|---|
| `dc-runner-spec` | migrated | `/specs/07_runner_behavior/**` |
| `data-contracts-bundle-spec` | migrated | `/specs/05_libraries/bundle_tooling/**`, `/specs/01_schema/**`, `/specs/02_contracts/**` |
| `data-contracts-bundler-spec` | migrated | `/specs/05_libraries/bundle_tooling/**`, `/specs/01_schema/**`, `/specs/02_contracts/**` |

## Path Mapping

| Old Path | New Path |
|---|---|
| `dc-runner-spec/specs/impl/**` | `data-contracts-library/specs/07_runner_behavior/impl/**` |
| `dc-runner-spec/specs/contract_sets/**` | `data-contracts-library/specs/07_runner_behavior/contract_sets/**` |
| `dc-runner-spec/specs/runner/**` | `data-contracts-library/specs/07_runner_behavior/runner/**` |
| `dc-runner-spec/specs/libraries/policy/**` | `data-contracts-library/specs/05_libraries/policy/**` |
| `data-contracts-bundle-spec/specs/schema/**` | `data-contracts-library/specs/01_schema/**` |
| `data-contracts-bundle-spec/specs/contract/**` | `data-contracts-library/specs/02_contracts/**` |
| `data-contracts-bundle-spec/fixtures/**` | `data-contracts-library/specs/05_libraries/bundle_tooling/fixtures/bundle_spec/**` |
| `data-contracts-bundle-spec/bundles/**` | `data-contracts-library/specs/05_libraries/bundle_tooling/bundles/**` |
| `data-contracts-bundler-spec/specs/schema/**` | `data-contracts-library/specs/01_schema/**` |
| `data-contracts-bundler-spec/specs/contract/**` | `data-contracts-library/specs/02_contracts/**` |
| `data-contracts-bundler-spec/specs/fixtures/**` | `data-contracts-library/specs/05_libraries/bundle_tooling/fixtures/bundler_spec/**` |

## Bundle IDs (Canonical)

- `data-contracts-library-core`
- `data-contracts-library-runner-behavior`
- `data-contracts-library-overlays`
- `data-contracts-library-bundle-tooling`
