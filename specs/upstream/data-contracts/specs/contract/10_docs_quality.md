# Docs Quality Contract (v1)

Documentation is a tested product surface.

## Layout and Naming

MUST:

- docs information architecture MUST follow canonical roots:
  - `docs/book`
  - `specs`
  - `docs/impl`
  - `docs/reviews`
- directory index files under `docs/**` MUST be named `index.md`.
- `README.md` under `docs/**` is forbidden.
- `.DS_Store` and similar OS/editor artifact files are forbidden in tracked docs paths.
- docs filenames MUST be lowercase and MUST NOT include spaces.
- active review workflows and prompts MUST use `docs/reviews` paths.
- the historical reviews archive root is archival-only and MUST NOT be used by active tooling guidance.

## Reference Surface

The canonical reference-manual narrative surface for v1 is:

- `docs/book/10_getting_started.md`
- `docs/book/20_case_model.md`
- `docs/book/30_assertion_model.md`
- `docs/book/40_spec_lang_authoring.md`
- `docs/book/50_library_authoring.md`
- `docs/book/60_runner_and_gates.md`
- `docs/book/70_governance_and_quality.md`
- `docs/book/80_troubleshooting.md`
- `docs/book/90_reference_guide.md`
- `docs/book/99_generated_reference_index.md`

Generated surfaces remain under `docs/book/91..98` and `docs/book/93*`.

MUST:

- reference-surface files required by governance MUST exist.
- `docs/book/reference_index.md` MUST match the chapter set/order in `docs/book/reference_manifest.yaml`.
- `docs/book/reference_manifest.yaml` MUST remain synchronized with generated reference artifacts.
- book chapter order MUST follow canonical author-first layered flow:
  - `10_getting_started.md`
  - `20_case_model.md`
  - `30_assertion_model.md`
  - `40_spec_lang_authoring.md`
  - `50_library_authoring.md`
  - `60_runner_and_gates.md`
  - `70_governance_and_quality.md`
  - `80_troubleshooting.md`
  - `90_reference_guide.md`
  - generated references through `99_generated_reference_index.md`

## Required Section Coverage

MUST:

- core reference chapters MUST include required section tokens defined by governance policy.
- missing required section tokens MUST fail governance checks.

## Metadata Schema

MUST:

- canonical reference chapters MUST include valid `doc-meta` metadata in front matter or `yaml doc-meta` fenced form.
- metadata MUST conform to `specs/schema/docs_schema_v1.md`.
- each metadata `owns_tokens` entry MUST have unique ownership across the canonical reference surface.
- each metadata `requires_tokens` entry MUST resolve to an owner doc and appear in owner text.

## Executable Example Policy

MUST:

- `yaml contract-spec` fenced examples in reference docs MUST parse as YAML.
- shell/python code examples in the reference surface MUST pass lightweight static validation.
- invalid examples MUST fail unless explicitly opted out.

Opt-out format:

- `DOCS-EXAMPLE-OPT-OUT: <reason>`

Rules:

- reason text MUST be specific and non-empty.
- opt-out applies only to nearby example blocks and SHOULD be temporary.

## Rust-First Examples Policy

MUST:

- primary command examples in active docs use rust lane entrypoints (`./runners/public/runner_adapter.sh --impl rust ...`).
- Python/PHP examples are allowed only in explicitly labeled `Compatibility (Non-Blocking)` sections.
- root `README.md` MUST remain gateway-oriented, link to canonical book/contract surfaces, and avoid legacy assertion syntax snippets.

## Contract/Schema/Book Synchronization

MUST:

- core assertion/import tokens used by authors and implementers MUST remain synchronized across:
  - `docs/book/30_assertion_model.md`
  - `specs/contract/03_assertions.md`
  - `specs/schema/schema_v1.md`

## Enforcement

Reference generation and graph artifacts:

- `scripts/docs_generate_all.py --build` is the canonical generator orchestrator.
- `scripts/docs_generate_all.py --check` is the canonical hard-fail freshness check.
- `scripts/docs_build_reference.py` renders:
  - `docs/book/reference_index.md`
  - `docs/book/reference_coverage.md`
  - `docs/book/docs_graph.json`
- API catalog generators produce:
  - `docs/book/91_appendix_runner_api_reference.md`
  - `docs/book/92_appendix_harness_type_reference.md`
  - `docs/book/93_appendix_spec_lang_builtin_catalog.md`
  - `docs/book/93a_std_core.md`
  - `docs/book/93b_std_logic.md`
  - `docs/book/93c_std_math.md`
  - `docs/book/93d_std_string.md`
  - `docs/book/93e_std_collection.md`
  - `docs/book/93f_std_object.md`
  - `docs/book/93g_std_type.md`
  - `docs/book/93h_std_set.md`
  - `docs/book/93i_std_json_schema_fn_null.md`
  - `docs/book/93j_library_symbol_reference.md`
  - `docs/book/93k_library_symbol_index.md`
  - `docs/book/93l_spec_case_reference.md`
  - `docs/book/93m_spec_case_index.md`
  - `docs/book/93n_spec_case_templates_reference.md`
  - `docs/book/94_appendix_contract_policy_reference.md`
  - `docs/book/95_appendix_traceability_reference.md`
  - `docs/book/96_appendix_governance_checks_reference.md`
  - `docs/book/97_appendix_metrics_reference.md`
  - `docs/book/98_appendix_spec_case_shape_reference.md`
- generated sections are read-only and delimited by markers.
- docs generator report artifacts are required:
  - `.artifacts/docs-generator-report.json`
  - `.artifacts/docs-generator-summary.md`

These requirements are enforced by governance checks and CI gates as hard failures.

## Release Guidance Policy

MUST:

- release guidance MUST point to executable gate entrypoints.
- sequential manual checklist choreography is an anti-pattern and MUST NOT be documented as normative process.
