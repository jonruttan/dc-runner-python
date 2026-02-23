# Docs Quality Contract (v1)

Documentation is a tested product surface.

## Layout and Naming

MUST:

- docs information architecture MUST follow canonical roots:
  - `docs/book`
  - `specs`
  - `docs/history/reviews` (archival review content)
- directory index files under `docs/**` MUST be named `index.md`.
- `README.md` under `docs/**` is forbidden.
- docs filenames MUST be lowercase and MUST NOT include spaces.

## User Guidance Requirements

MUST:

- root `README.md` MUST clearly describe what the repository is and is not.
- root `README.md` MUST include task-based usage paths for users.
- root `README.md` MUST link to canonical docs/book and contracts surfaces.
- root `README.md` MUST NOT be Makefile-onboarding cookbook content.
- chapter `docs/book/10_getting_started.md` MUST function as launch page.
- chapter `docs/book/90_reference_guide.md` MUST map guides to normative
  contract/schema sources.

## Visual Aids Requirements

MUST:

- `docs/book/05_what_is_data_contracts.md`,
  `docs/book/15_spec_lifecycle.md`, and
  `docs/book/25_system_topology.md`
  each include at least one Mermaid diagram block.
- core guide chapters for gates/debugging/schema/ci/status include Mermaid where
  designated by docs governance.

## Usage Guide Structure

MUST:

- each `docs/book/guides/guide_*.md` include:
  - `## When to read this`
  - `## What you will do`
  - `## Step-by-step`
  - `## Common failure signals`
  - `## Normative refs`

## Control-Plane Language Policy

MUST:

- active docs in this repository use implementation-agnostic control-plane
  language.
- runtime execution ownership is referenced as external (`dc-runner-*`).
- active docs MUST NOT use rust-primary required-lane language for this
  repository.

## Enforcement

MUST:

- `docs/book/reference_manifest.yaml`, `docs/book/reference_index.md`, and
  `docs/book/reference_coverage.md` remain synchronized.
- docs quality checks are enforced by governance cases and CI checks.
