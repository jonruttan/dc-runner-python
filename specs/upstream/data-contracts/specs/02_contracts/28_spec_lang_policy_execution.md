# Spec-Lang Policy Execution Contract (v1)

Defines the policy execution boundary for control-plane governance.

## Core Rule

Policy verdict logic MUST be encoded in governance/conformance spec assertions
and evaluated through spec-lang execution surfaces. For multi-step policy
domains, verdict flow MUST be decomposed into constituent cases linked through
`harness.chain`.

## Boundary

Shell scripts in this repository are limited to transport and orchestration:

- file I/O and artifact staging
- environment parsing
- process invocation
- network fetch/checksum plumbing

Shell scripts MUST NOT be the source of final policy verdict semantics for
governance domains covered by executable spec checks.

## Extractor Model

Extractor scripts MAY emit normalized artifacts to `.artifacts/` that are used
as policy inputs, including:

- `/.artifacts/governance-catalog-validate.json`
- `/.artifacts/spec-schema-pin-validate.json`
- `/.artifacts/governance-optional-report.json`

Extractor scripts are data producers; pass/fail policy outcomes are owned by
spec checks.

## Chained Policy Composition

Policy domains that aggregate multiple signals (catalog integrity, schema-pin
integrity, optional reporting integrity, ingest integrity, CI gate integrity)
MUST use chain entry cases:

- chain entry case declares `harness.chain.steps` with explicit `class` and `ref`
- constituent step cases remain independently addressable contracts
- shared predicates are exported from policy libraries and reused by chain entry
  cases

Chain entry cases are grouped by governance domain:

- `/specs/04_governance/cases/core/spec_core/`
- `/specs/04_governance/cases/core/runner_contract/`
- `/specs/04_governance/cases/core/project_docs/`

Runner-ingestible domain packs:

- `/specs/00_core/packs/runner_contract_pack_v1.yaml`
- `/specs/00_core/packs/spec_core_maintenance_pack_v1.yaml`
- `/specs/00_core/packs/project_docs_maintenance_pack_v1.yaml`

## Artifact Compatibility

During normalization and after cutover:

- existing artifact file paths remain stable
- existing top-level JSON keys remain stable
- CI may add parity artifacts, but must not break canonical artifact consumers

## Enforcement

Governance checks MUST enforce:

- spec-lang policy-source requirements
- shell decision-branch forbiddance for covered policy domains
- artifact compatibility for extractor outputs
- infra boundary constraints for transport scripts
- presence and validity of chain entry policy cases
- policy-library symbol resolution for chain entry checks

## Ingest Flag Compatibility

`runner_status_ingest.sh --enforce-freshness` is accepted for CLI compatibility.
Blocking policy verdicts MUST be determined by governance/spec checks consuming
ingest artifacts, not by direct shell-policy exits.
