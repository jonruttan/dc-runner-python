# Objective Metrics Schema (v1)

Schema for objective scorecard configuration.

## Manifest File

Canonical manifest path:

- `specs/governance/metrics/objective_manifest.yaml`

Root shape:

```yaml
version: 1
thresholds:
  green_min: 0.75
  yellow_min: 0.5
objectives: []
correction_policy:
  delta_drop_threshold: 0.05
  review_window_baselines: 2
```

## `objectives[]`

Required fields:

- `id` (string)
- `name` (string)
- `primary` (mapping)
- `tripwires` (list[mapping])

Optional fields:

- `counters` (list[mapping])
- `primary_weight` (number)
- `counter_weight` (number)
- `course_correction` (mapping)

### `primary` / `counters[]` mapping

Required fields:

- `id` (required for counters)
- `source` (one of: `spec_portability`, `spec_lang_adoption`, `runner_independence`, `docs_operability`, `contract_assertions`, `derived`)
- `field` (dotted numeric field path within source)

Optional fields:

- `mode`: `direct` | `one_minus` (default `direct`)
- `scale`: positive number (default `1.0`)

### `tripwires[]` mapping

Required fields:

- `check_id` (governance check id)

Optional fields:

- `reason` (human-readable trigger rationale)

### `course_correction` mapping

Optional fields:

- `action` (single-line required action when objective is yellow/red)
- `pending_spec_template` (reference ID/path)

## Baseline Notes Schema

File:

- `specs/governance/metrics/baseline_update_notes.yaml`

Shape:

```yaml
version: 1
entries:
- baseline: specs/governance/metrics/objective_scorecard_baseline.json
  sha256: <64 hex chars>
  rationale: <non-empty>
  measurement_model_change: 'no'
```
