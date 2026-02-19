# 24 Runtime Profiling Contract

## Scope

- Defines the canonical runtime profiling artifact for timeout diagnosis.
- Applies to Python and Rust runner implementations.
- Profiling is opt-in and disabled by default.

## Activation

- `--profile-level off|basic|detailed|debug` (default `off`)
- `--profile-out <path>` (default `/.artifacts/run-trace.json`)
- `--profile-summary-out <path>` (default `/.artifacts/run-trace-summary.md`)
- `--profile-heartbeat-ms <int>` (default `1000`)
- `--profile-stall-threshold-ms <int>` (default `10000`)

Environment equivalents:

- `SPEC_RUNNER_PROFILE_LEVEL`
- `SPEC_RUNNER_PROFILE_OUT`
- `SPEC_RUNNER_PROFILE_SUMMARY_OUT`
- `SPEC_RUNNER_PROFILE_HEARTBEAT_MS`
- `SPEC_RUNNER_PROFILE_STALL_THRESHOLD_MS`

Liveness controls (governance-first):

- `--liveness-level off|basic|strict`
- `--liveness-stall-ms <int>` (default `30000`)
- `--liveness-min-events <int>` (default `1`)
- `--liveness-hard-cap-ms <int>` (default `1800000`)
- `--liveness-kill-grace-ms <int>` (default `5000`)

Environment equivalents:

- `SPEC_RUNNER_LIVENESS_LEVEL`
- `SPEC_RUNNER_LIVENESS_STALL_MS`
- `SPEC_RUNNER_LIVENESS_MIN_EVENTS`
- `SPEC_RUNNER_LIVENESS_HARD_CAP_MS`
- `SPEC_RUNNER_LIVENESS_KILL_GRACE_MS`

Fail-fast gate controls:

- `--fail-fast` (default `true`)
- `--continue-on-fail` (disables fail-fast)
- `--profile-on-fail off|basic|detailed` (default `basic`)
- `SPEC_RUNNER_FAIL_FAST`
- `SPEC_RUNNER_PROFILE_ON_FAIL`

## Artifact

- Schema: `/specs/schema/run_trace_v1.yaml`
- JSON artifact: `/.artifacts/run-trace.json`
- Summary artifact: `/.artifacts/run-trace-summary.md`

Required top-level fields:

- `version`, `run_id`, `runner_impl`, `started_at`, `ended_at`, `status`
- `command`, `args`, `env_profile`
- `spans`, `events`, `summary`

Fail-fast gate summary payload contract:

- `fail_fast_enabled: bool`
- `first_failure_step: string|null`
- `aborted_after_step: string|null`
- `skipped_step_count: int`
- step rows MAY include `skip_reason` and `blocked_by` when status is `skipped`.
- step rows SHOULD include triage metadata for governance step:
  - `triage_attempted: bool`
  - `triage_mode: broad|targeted|both|not_run`
  - `triage_result: pass|fail|stalled|not_run`
  - `failing_check_ids: list[string]`
  - `failing_check_prefixes: list[string]`
  - `stall_detected: bool`
  - `stall_phase: string|null`

On failing `ci-gate-summary` runs with profile-on-fail enabled:

- `/.artifacts/run-trace.json` MUST be written.
- `/.artifacts/run-trace-summary.md` MUST be written.

## Required Span Taxonomy

- `run.total`
- `runner.dispatch`
- `case.run`
- `case.chain`
- `case.harness`
- `check.execute`
- `subprocess.exec`
- `subprocess.wait`

## Required Event Kinds

- `heartbeat`
- `stall_warning`
- `watchdog`
- `subprocess_state`
- `checkpoint`

## Timeout Reason Tokens

- `timeout.subprocess.wait`
- `timeout.subprocess.io_drain`
- `timeout.case.harness`
- `timeout.case.chain`
- `stall.runner.no_progress`
- `stall.subprocess.no_output_no_event`
- `timeout.hard_cap.emergency`
- `watchdog.kill.term`
- `watchdog.kill.killed`

## Timeout Environment Inputs

- Governance timeout behavior is controlled by liveness settings and
  adapter/runtime timeout inputs.

## Redaction

- Profiling artifacts MUST NOT expose raw secret values.
- Secret-like keys (`token`, `secret`, `password`, `authorization`, `cookie`, `key`) MUST be redacted.
- `env_profile` may include metadata (set/length/hash) but not raw values.
