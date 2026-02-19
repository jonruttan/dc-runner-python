from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import contextlib
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import yaml

from spec_runner.conformance import ConformanceResult, compare_conformance_results, load_expected_results
from spec_runner.conformance_parity import (
    ParityConfig,
    build_parity_artifact,
    run_parity_check,
    run_python_report,
)
from spec_runner.docs_generate_specs import main as _docs_generate_specs_main
from spec_runner.docs_inventory import build_inventory as _build_docs_inventory


def _write_artifact(path: Path, artifact: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compare_conformance_parity_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run Python/PHP conformance and report normalized parity diffs by case id."
    )
    ap.add_argument("--cases", default="specs/conformance/cases")
    ap.add_argument("--php-runner", default="runners/php/conformance_runner.php")
    ap.add_argument("--python-runner", default="spec_runner.python_conformance_runner")
    ap.add_argument("--out", default="")
    ap.add_argument("--case-formats", default="md")
    ap.add_argument("--php-timeout-seconds", type=int, default=30)
    ap.add_argument("--python-timeout-seconds", type=int, default=30)
    ap.add_argument("--python-only", action="store_true")
    ns = ap.parse_args(argv)
    out_path = Path(str(ns.out)).resolve() if str(ns.out).strip() else None

    if not ns.python_only and shutil.which("php") is None:
        msg = "php executable not found in PATH"
        if out_path is not None:
            _write_artifact(out_path, build_parity_artifact([msg]))
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    case_formats = {x.strip() for x in str(ns.case_formats).split(",") if x.strip()}
    if not case_formats:
        msg = "--case-formats requires at least one format"
        if out_path is not None:
            _write_artifact(out_path, build_parity_artifact([msg]))
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    if ns.python_only:
        try:
            python_payload = run_python_report(
                Path(ns.cases),
                str(ns.python_runner),
                case_formats=case_formats,
                timeout_seconds=int(ns.python_timeout_seconds),
            )
            expected = load_expected_results(
                Path(ns.cases),
                implementation="python",
                case_formats=case_formats,
            )
            python_actual = [
                ConformanceResult(
                    id=str(r.get("id", "")),
                    status=str(r.get("status", "")),
                    category=None if r.get("category") is None else str(r.get("category")),
                    message=None if r.get("message") is None else str(r.get("message")),
                )
                for r in python_payload.get("results", [])
            ]
            errs = [f"python vs expected: {e}" for e in compare_conformance_results(expected, python_actual)]
        except RuntimeError as exc:
            if out_path is not None:
                _write_artifact(out_path, build_parity_artifact([str(exc)]))
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    else:
        cfg = ParityConfig(
            cases_dir=Path(ns.cases),
            php_runner=Path(ns.php_runner),
            python_runner=str(ns.python_runner),
            case_formats=case_formats,
            python_timeout_seconds=int(ns.python_timeout_seconds),
            php_timeout_seconds=int(ns.php_timeout_seconds),
        )
        try:
            errs = run_parity_check(cfg)
        except RuntimeError as exc:
            if out_path is not None:
                _write_artifact(out_path, build_parity_artifact([str(exc)]))
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    if out_path is not None:
        _write_artifact(out_path, build_parity_artifact(errs))
    if errs:
        print("ERROR: conformance parity check failed", file=sys.stderr)
        for err in errs:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"OK: conformance parity matched for {Path(ns.cases)}")
    return 0


def docs_generate_all_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate and verify docs surfaces via spec-driven docs.generate cases.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    ap.add_argument("--surface", default="")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--report-out", default=".artifacts/docs-generator-report.json")
    ap.add_argument("--summary-out", default=".artifacts/docs-generator-summary.md")
    ap.add_argument("--timing-out", default=".artifacts/docs-generate-timing.json")
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--profile-out", default=".artifacts/docs-generate-profile.json")
    ap.add_argument("--profile-level", default="")
    ap.add_argument("--profile-summary-out", default="")
    ap.add_argument("--profile-heartbeat-ms", type=int, default=0)
    ap.add_argument("--profile-stall-threshold-ms", type=int, default=0)
    ns = ap.parse_args(argv)

    forwarded = [
        "--check" if ns.check else "--build",
        "--report-out",
        str(ns.report_out),
        "--summary-out",
        str(ns.summary_out),
        "--timing-out",
        str(ns.timing_out),
    ]
    if bool(ns.profile):
        forwarded.append("--profile")
        forwarded += ["--profile-out", str(ns.profile_out)]
    if str(ns.profile_level).strip():
        forwarded += ["--profile-level", str(ns.profile_level).strip()]
    if str(ns.profile_summary_out).strip():
        forwarded += ["--profile-summary-out", str(ns.profile_summary_out).strip()]
    if int(ns.profile_heartbeat_ms or 0) > 0:
        forwarded += ["--profile-heartbeat-ms", str(int(ns.profile_heartbeat_ms))]
    if int(ns.profile_stall_threshold_ms or 0) > 0:
        forwarded += ["--profile-stall-threshold-ms", str(int(ns.profile_stall_threshold_ms))]
    if int(ns.jobs) != 0:
        forwarded += ["--jobs", str(int(ns.jobs))]
    if str(ns.surface).strip():
        forwarded += ["--surface", str(ns.surface).strip()]
    return int(_docs_generate_specs_main(forwarded))


def _env_bool(name: str, default: bool) -> bool:
    raw = str(os.environ.get(name, "")).strip().lower()
    if not raw:
        return default
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


def _coerce_profile_level(raw: str) -> str:
    level = str(raw or "").strip().lower()
    if level in {"off", "basic", "detailed", "debug"}:
        return level
    return "off"


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(cast(Any, value))
    except (TypeError, ValueError):
        return default


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(cast(Any, value))
    except (TypeError, ValueError):
        return default


def _write_fail_profile_artifacts(
    *,
    trace_path: Path,
    summary_path: Path,
    payload: dict[str, object],
) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    steps = payload.get("steps")
    normalize_mode = payload.get("normalize_mode")
    normalized_file_count = payload.get("normalized_file_count")
    run_trace = {
        "version": 1,
        "run_id": f"gate-{int(time.time() * 1000)}",
        "runner_impl": payload.get("runner_impl"),
        "started_at": payload.get("started_at"),
        "ended_at": payload.get("finished_at"),
        "status": payload.get("status"),
        "command": "ci-gate-summary",
        "args": [],
        "env_profile": {},
        "spans": [
            {
                "span_id": "s1",
                "parent_span_id": None,
                "kind": "run",
                "name": "run.total",
                "phase": "run.total",
                "start_ns": 0,
                "end_ns": _to_int(payload.get("total_duration_ms", 0)) * 1_000_000,
                "duration_ms": _to_float(payload.get("total_duration_ms", 0)),
                "status": "ok" if payload.get("status") == "pass" else "error",
                "attrs": {
                    "source": "ci-gate-summary",
                    "normalize_mode": normalize_mode,
                    "normalized_file_count": normalized_file_count,
                },
                "error": None,
            }
        ],
        "events": payload.get("events", []),
        "summary": {
            "step_count": len(steps) if isinstance(steps, list) else 0,
            "failed_step": payload.get("first_failure_step"),
        },
    }
    trace_path.write_text(json.dumps(run_trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = []
    if isinstance(steps, list):
        for row in steps:
            if isinstance(row, dict):
                rows.append(
                    (
                        str(row.get("name", "")),
                        str(row.get("status", "")),
                        str(row.get("duration_ms", "")),
                    )
                )
    md = [
        "# Run Trace Summary",
        "",
        f"- status: `{payload.get('status', 'unknown')}`",
        f"- first_failure_step: `{payload.get('first_failure_step', '')}`",
        f"- skipped_step_count: `{payload.get('skipped_step_count', 0)}`",
        "",
        "## Steps",
        "",
        "| step | status | duration_ms |",
        "|---|---|---|",
    ]
    for name, status, duration in rows:
        md.append(f"| `{name}` | `{status}` | `{duration}` |")
    md.append("")
    md.append("## Suggested Next Command")
    md.append("")
    md.append("- `./runners/public/runner_adapter.sh --impl rust --profile-level detailed ci-gate-summary`")
    summary_path.write_text("\n".join(md) + "\n", encoding="utf-8")


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _runner_command(runner_bin: str, runner_impl: str, subcommand: str) -> list[str]:
    normalized = runner_bin.replace("\\", "/")
    if normalized.endswith("/runners/public/runner_adapter.sh") or normalized in {
        "runners/public/runner_adapter.sh",
        "./runners/public/runner_adapter.sh",
    }:
        return [runner_bin, "--impl", runner_impl, subcommand]
    return [runner_bin, subcommand]


def _python_command() -> list[str]:
    override = str(os.environ.get("SPEC_CI_PYTHON", "")).strip()
    if override:
        return [override]
    venv = str(os.environ.get("VIRTUAL_ENV", "")).strip()
    if venv:
        p = Path(venv) / "bin" / "python"
        if p.exists():
            return [p.as_posix()]
    local = Path(".venv/bin/python")
    if local.exists():
        return [local.as_posix()]
    return [sys.executable or "python3"]


def _runner_command_with_liveness(
    runner_bin: str,
    runner_impl: str,
    subcommand: str,
    *,
    level: str,
    stall_ms: str,
    kill_grace_ms: str,
    hard_cap_ms: str,
) -> list[str]:
    normalized = runner_bin.replace("\\", "/")
    if normalized.endswith("/runners/public/runner_adapter.sh") or normalized in {
        "runners/public/runner_adapter.sh",
        "./runners/public/runner_adapter.sh",
    }:
        return [
            runner_bin,
            "--impl",
            runner_impl,
            "--liveness-level",
            level,
            "--liveness-stall-ms",
            stall_ms,
            "--liveness-kill-grace-ms",
            kill_grace_ms,
            "--liveness-hard-cap-ms",
            hard_cap_ms,
            subcommand,
        ]
    return [runner_bin, subcommand]


def _collect_changed_paths() -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    def _push_lines(raw: str) -> None:
        for line in raw.splitlines():
            rel = line.strip()
            if not rel:
                continue
            if rel in seen:
                continue
            seen.add(rel)
            out.append(rel)

    try:
        upstream = (
            subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
                check=False,
                capture_output=True,
                text=True,
            ).stdout
            or ""
        ).strip()
    except Exception:
        upstream = ""
    if upstream:
        diff = subprocess.run(
            ["git", "diff", "--name-only", f"{upstream}...HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if diff.returncode == 0:
            _push_lines(diff.stdout or "")
    for cmd in (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if proc.returncode == 0:
            _push_lines(proc.stdout or "")
    return out


def _normalize_step_metadata(command: list[str]) -> dict[str, object]:
    mode = "full_tree"
    selected_paths: list[str] = []
    i = 0
    while i < len(command):
        token = command[i]
        if token == "--changed-only":
            mode = "changed_only"
            i += 1
            continue
        if token == "--paths" and i + 1 < len(command):
            mode = "changed_only"
            selected_paths.extend([x.strip() for x in command[i + 1].split(",") if x.strip()])
            i += 2
            continue
        if token == "--path" and i + 1 < len(command):
            mode = "changed_only"
            one = command[i + 1].strip()
            if one:
                selected_paths.append(one)
            i += 2
            continue
        i += 1
    if mode == "changed_only" and not selected_paths:
        selected_paths = _collect_changed_paths()
    return {
        "normalize_mode": mode,
        "normalized_file_count": len(selected_paths) if mode == "changed_only" else None,
    }


def _default_steps(runner_bin: str, runner_impl: str) -> list[tuple[str, list[str]]]:
    broad_liveness_level = str(os.environ.get("SPEC_CI_GOV_BROAD_LIVENESS_LEVEL", "strict"))
    broad_liveness_stall_ms = str(os.environ.get("SPEC_CI_GOV_BROAD_LIVENESS_STALL_MS", "5000"))
    broad_liveness_kill_grace_ms = str(os.environ.get("SPEC_CI_GOV_BROAD_LIVENESS_KILL_GRACE_MS", "1000"))
    broad_liveness_hard_cap_ms = str(os.environ.get("SPEC_CI_GOV_BROAD_LIVENESS_HARD_CAP_MS", "120000"))
    py = _python_command()
    steps: list[tuple[str, list[str]]] = [
        (
            "governance_broad",
            _runner_command_with_liveness(
                runner_bin,
                runner_impl,
                "governance-broad-native",
                level=broad_liveness_level,
                stall_ms=broad_liveness_stall_ms,
                kill_grace_ms=broad_liveness_kill_grace_ms,
                hard_cap_ms=broad_liveness_hard_cap_ms,
            ),
        ),
        ("runner_certify_rust", _runner_command(runner_bin, runner_impl, "runner-certify", "--runner", "rust")),
        ("docs_generate_check", _runner_command(runner_bin, runner_impl, "docs-generate-check")),
        ("docs_lint", _runner_command(runner_bin, runner_impl, "docs-lint")),
        ("normalize_check", _runner_command(runner_bin, runner_impl, "normalize-check")),
        ("schema_registry_build", _runner_command(runner_bin, runner_impl, "schema-registry-build")),
        ("schema_registry_check", _runner_command(runner_bin, runner_impl, "schema-registry-check")),
        ("schema_docs_check", _runner_command(runner_bin, runner_impl, "schema-docs-check")),
        (
            "spec_lang_lint_full",
            [*py, "-m", "spec_runner.spec_lang_commands", "spec-lang-lint", "--cases", "specs"],
        ),
        (
            "library_symbol_metadata_lint",
            [*py, "-m", "spec_runner.spec_lang_commands", "spec-lang-lint", "--cases", "specs/libraries"],
        ),
        (
            "spec_lang_format_check_full",
            [*py, "-m", "spec_runner.spec_lang_commands", "spec-lang-format", "--check", "specs"],
        ),
        (
            "library_symbol_catalog_sync",
            [*py, "-m", "spec_runner.spec_lang_commands", "generate-library-symbol-catalog", "--check"],
        ),
        (
            "spec_case_catalog_sync",
            [*py, "-m", "spec_runner.spec_lang_commands", "generate-spec-case-catalog", "--check"],
        ),
        (
            "spec_domain_grouping_sync",
            [*py, "-m", "spec_runner.spec_lang_commands", "generate-spec-case-catalog", "--check"],
        ),
        ("ruff", _runner_command(runner_bin, runner_impl, "lint")),
        ("mypy", _runner_command(runner_bin, runner_impl, "typecheck")),
        ("compileall", _runner_command(runner_bin, runner_impl, "compilecheck")),
    ]
    if _env_bool("SPEC_CI_INCLUDE_CONFORMANCE_PARITY", False):
        steps.append(("conformance_parity", _runner_command(runner_bin, runner_impl, "conformance-parity")))
    return steps


def _run_command(command: list[str]) -> int:
    proc = subprocess.run(command, check=False)
    return int(proc.returncode)


def _run_steps(
    steps: list[tuple[str, list[str]]],
    *,
    fail_fast: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]], str | None]:
    rows: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    first_failure_step: str | None = None
    aborted = False
    for name, command in steps:
        if aborted:
            rows.append(
                {
                    "name": name,
                    "command": command,
                    "status": "skipped",
                    "exit_code": None,
                    "duration_ms": 0,
                    "skip_reason": "fail_fast.after_failure",
                    "blocked_by": first_failure_step,
                }
            )
            events.append(
                {
                    "ts_ns": time.monotonic_ns(),
                    "kind": "checkpoint",
                    "span_id": "run.total",
                    "attrs": {"event": "gate.step.skipped", "step": name, "blocked_by": first_failure_step},
                }
            )
            continue
        events.append(
            {
                "ts_ns": time.monotonic_ns(),
                "kind": "checkpoint",
                "span_id": "run.total",
                "attrs": {"event": "gate.step.start", "step": name},
            }
        )
        step_meta: dict[str, object] = {}
        if name == "normalize_check":
            step_meta = _normalize_step_metadata(command)
            attrs = events[-1].get("attrs")
            if isinstance(attrs, dict):
                attrs["normalize_mode"] = step_meta.get("normalize_mode")
                attrs["normalized_file_count"] = step_meta.get("normalized_file_count")
        print(f"[gate] {name}: {' '.join(command)}")
        t0 = time.perf_counter()
        code = _run_command(command)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        status = "pass" if code == 0 else "fail"
        rows.append(
            {
                "name": name,
                "command": command,
                "status": status,
                "exit_code": code,
                "duration_ms": duration_ms,
                **step_meta,
            }
        )
        if name == "governance_broad":
            rows[-1]["triage_phase"] = "broad"
            rows[-1]["broad_required"] = True
        events.append(
            {
                "ts_ns": time.monotonic_ns(),
                "kind": "checkpoint",
                "span_id": "run.total",
                "attrs": {"event": f"gate.step.{status}", "step": name, "exit_code": code},
            }
        )
        if status == "fail" and first_failure_step is None:
            first_failure_step = name
            if fail_fast:
                aborted = True
                events.append(
                    {
                        "ts_ns": time.monotonic_ns(),
                        "kind": "checkpoint",
                        "span_id": "run.total",
                        "attrs": {"event": "gate.fail_fast.abort", "after_step": name},
                    }
                )
    return rows, events, first_failure_step


def _collect_unit_test_opt_out(root: Path) -> dict[str, int]:
    tests_root = root / "tests"
    baseline_path = root / "specs/governance/metrics/unit_test_opt_out_baseline.json"
    prefix = "# SPEC-OPT-OUT:"
    total = 0
    opted_out = 0
    if tests_root.exists():
        for path in sorted(tests_root.glob("test_*_unit.py")):
            if not path.is_file():
                continue
            total += 1
            first_non_empty = ""
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    first_non_empty = line.strip()
                    break
            if first_non_empty.startswith(prefix):
                opted_out += 1
    baseline_max = 0
    if baseline_path.exists():
        try:
            payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("max_opt_out_file_count"), int):
            baseline_max = int(payload["max_opt_out_file_count"])
    return {
        "total_unit_test_files": total,
        "opt_out_file_count": opted_out,
        "baseline_max_opt_out_file_count": baseline_max,
    }


def _evaluate_gate_policy(*, rows: list[dict[str, object]]) -> bool:
    return all(str(row.get("status", "")) == "pass" for row in rows)


def ci_gate_summary_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run local CI gate checks and emit machine-readable summary JSON."
    )
    ap.add_argument(
        "--out",
        default=".artifacts/gate-summary.json",
        help="Output path for gate summary JSON (default: .artifacts/gate-summary.json)",
    )
    ap.add_argument("--runner-bin", required=True, help="Path to runner interface command")
    ap.add_argument(
        "--runner-impl",
        default=os.environ.get("SPEC_RUNNER_IMPL", "rust"),
        help="Runner implementation mode passed to runner adapter (default: rust).",
    )
    ap.add_argument(
        "--trace-out",
        default=os.environ.get("SPEC_RUNNER_TRACE_OUT", ""),
        help="Optional output path for command execution trace JSON.",
    )
    ap.add_argument(
        "--fail-fast",
        action="store_true",
        default=False,
        help="Stop after first failing gate step (default: true unless --continue-on-fail).",
    )
    ap.add_argument(
        "--continue-on-fail",
        action="store_true",
        help="Disable fail-fast and execute all gate steps.",
    )
    ap.add_argument(
        "--profile-on-fail",
        default=os.environ.get("SPEC_RUNNER_PROFILE_ON_FAIL", "basic"),
        help="off|basic|detailed for fail-fast diagnostics (default: basic).",
    )
    ns = ap.parse_args(argv)

    out_path = Path(str(ns.out))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fail_fast_env_default = _env_bool("SPEC_RUNNER_FAIL_FAST", True)
    fail_fast_enabled = not bool(ns.continue_on_fail)
    if ns.fail_fast:
        fail_fast_enabled = True
    elif not ns.continue_on_fail:
        fail_fast_enabled = fail_fast_env_default
    profile_on_fail = _coerce_profile_level(str(ns.profile_on_fail))

    started = _now_iso_utc()
    t0 = time.perf_counter()
    steps, events, first_failure_step = _run_steps(
        _default_steps(str(ns.runner_bin), str(ns.runner_impl)),
        fail_fast=fail_fast_enabled,
    )
    verdict = _evaluate_gate_policy(rows=steps)
    first_failure = next(
        (
            _to_int(step["exit_code"])
            for step in steps
            if step.get("exit_code") is not None and _to_int(step["exit_code"]) != 0
        ),
        1,
    )
    exit_code = 0 if verdict else first_failure
    total_duration_ms = int((time.perf_counter() - t0) * 1000)
    finished = _now_iso_utc()

    payload: dict[str, object] = {
        "version": 1,
        "status": "pass" if verdict else "fail",
        "policy_verdict": "pass" if verdict else "fail",
        "policy_case": None,
        "policy_expr": None,
        "started_at": started,
        "finished_at": finished,
        "total_duration_ms": total_duration_ms,
        "steps": steps,
        "events": events,
        "fail_fast_enabled": bool(fail_fast_enabled),
        "first_failure_step": first_failure_step,
        "aborted_after_step": first_failure_step if (first_failure_step and fail_fast_enabled) else None,
        "skipped_step_count": sum(1 for step in steps if str(step.get("status", "")) == "skipped"),
        "runner_bin": str(ns.runner_bin),
        "runner_impl": str(ns.runner_impl),
        "unit_test_opt_out": _collect_unit_test_opt_out(Path.cwd()),
    }
    normalize_step = next((s for s in steps if s.get("name") == "normalize_check"), None)
    if isinstance(normalize_step, dict):
        payload["normalize_mode"] = normalize_step.get("normalize_mode", "full_tree")
        payload["normalized_file_count"] = normalize_step.get("normalized_file_count")
    governance_step = next((s for s in steps if s.get("name") == "governance_broad"), None)
    if isinstance(governance_step, dict):
        payload["triage_attempted"] = bool(governance_step.get("triage_attempted", False))
        payload["triage_mode"] = governance_step.get("triage_mode", "not_run")
        payload["triage_result"] = governance_step.get("triage_result", "not_run")
        payload["failing_check_ids"] = governance_step.get("failing_check_ids", [])
        payload["failing_check_prefixes"] = governance_step.get("failing_check_prefixes", [])
        payload["stall_detected"] = bool(governance_step.get("stall_detected", False))
        payload["stall_phase"] = governance_step.get("stall_phase")
    else:
        payload["triage_attempted"] = False
        payload["triage_mode"] = "not_run"
        payload["triage_result"] = "not_run"
        payload["failing_check_ids"] = []
        payload["failing_check_prefixes"] = []
        payload["stall_detected"] = False
        payload["stall_phase"] = None
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    trace_out = str(ns.trace_out or "").strip()
    if trace_out:
        trace_path = Path(trace_out)
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_payload = {
            "version": 1,
            "runner_bin": str(ns.runner_bin),
            "runner_impl": str(ns.runner_impl),
            "steps": steps,
            "events": events,
            "fail_fast_enabled": bool(fail_fast_enabled),
            "first_failure_step": first_failure_step,
        }
        trace_path.write_text(json.dumps(trace_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[gate] trace: {trace_path}")
    if exit_code != 0 and profile_on_fail != "off":
        _write_fail_profile_artifacts(
            trace_path=Path(".artifacts/run-trace.json"),
            summary_path=Path(".artifacts/run-trace-summary.md"),
            payload=payload,
        )
        print("[gate] profile: .artifacts/run-trace.json")
        print("[gate] profile-summary: .artifacts/run-trace-summary.md")
    print(f"[gate] summary: {out_path}")
    return exit_code


_FORBIDDEN_TOKENS = {
    "spec-test": r"\bspec-test\b",
    "policy_evaluate": r"\bpolicy_evaluate\b",
}

_SOURCE_OF_TRUTH_RE = re.compile(r"^Source of truth:\s*([^\s]+)\s*$", re.IGNORECASE)
_EXPECTED_SPEC_INDEX_LINKS = {
    "/specs/schema/index.md",
    "/specs/contract/index.md",
    "/specs/governance/index.md",
    "/specs/libraries/index.md",
    "/specs/impl/index.md",
    "/specs/current.md",
}


def _load_check_map(root: Path) -> dict[str, Any]:
    path = root / "specs/governance/check_catalog_map_v1.yaml"
    if not path.exists():
        return {}
    prefixes: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("check_prefix:"):
            continue
        value = stripped.split(":", 1)[1].strip().strip("'\"")
        if value:
            prefixes.append(value)
    return {"families": [{"check_prefix": p} for p in prefixes]}


def _check_source_of_truth(root: Path) -> list[str]:
    seen: dict[str, str] = {}
    violations: list[str] = []
    for path in sorted((root / "docs").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = _SOURCE_OF_TRUTH_RE.match(line.strip())
            if not match:
                continue
            key = match.group(1).strip()
            prev = seen.get(key)
            if prev and prev != rel:
                violations.append(
                    f"{rel}:{line_no}: duplicate source-of-truth marker '{key}' already declared in {prev}"
                )
            else:
                seen[key] = rel
    return violations


def _check_forbidden_tokens(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted((root / "docs").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for label, pattern in _FORBIDDEN_TOKENS.items():
            if re.search(pattern, text):
                violations.append(f"{rel}: contains forbidden stale token '{label}'")
    return violations


def _check_spec_index_contract(root: Path) -> list[str]:
    path = root / "specs/index.md"
    if not path.exists():
        return ["specs/index.md missing"]
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []
    for rel in _EXPECTED_SPEC_INDEX_LINKS:
        if rel not in text:
            violations.append(f"specs/index.md missing canonical link {rel}")
    return violations


def _check_governance_family_map(root: Path) -> list[str]:
    mapping = _load_check_map(root)
    families = mapping.get("families") if isinstance(mapping, dict) else None
    if not isinstance(families, list) or not families:
        return ["specs/governance/check_catalog_map_v1.yaml must declare non-empty families list"]

    prefixes: set[str] = set()
    for entry in families:
        if not isinstance(entry, dict):
            return ["specs/governance/check_catalog_map_v1.yaml families entries must be mappings"]
        prefix = str(entry.get("check_prefix", "")).strip()
        if not prefix:
            return ["specs/governance/check_catalog_map_v1.yaml families[].check_prefix required"]
        prefixes.add(prefix)

    violations: list[str] = []
    for path in sorted((root / "specs/governance/cases/core").glob("*.spec.md")):
        name = path.name
        stem = name[:-8] if name.endswith(".spec.md") else name
        if "_" not in stem:
            violations.append(f"{path.relative_to(root).as_posix()}: expected '<family>_*.spec.md' naming")
            continue
        family = stem.split("_", 1)[0]
        check_prefix = family + "."
        if check_prefix not in prefixes:
            violations.append(
                f"{path.relative_to(root).as_posix()}: no check-family mapping for prefix '{check_prefix}'"
            )
    return violations


def _run_docs_generate_check(root: Path) -> list[str]:
    _ = root
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
        code = int(docs_generate_all_main(["--check"]))
    if code == 0:
        return []
    out = capture.getvalue().strip()
    if out:
        return [f"docs_generate_all --check failed:\n{out}"]
    return ["docs_generate_all --check failed with no output"]


def check_docs_freshness_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strict specs freshness and organization checks")
    parser.add_argument("--strict", action="store_true", help="return non-zero when violations are detected")
    parser.add_argument("--out", default=".artifacts/docs-freshness-report.json", help="report output path")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[3]
    inventory = _build_docs_inventory(root)
    violations: list[str] = []

    for item in inventory.get("missing_links", []):
        if isinstance(item, dict):
            violations.append(f"{item.get('file')}: broken link target {item.get('target')}")

    violations.extend(_check_source_of_truth(root))
    violations.extend(_check_forbidden_tokens(root))
    violations.extend(_check_spec_index_contract(root))
    violations.extend(_check_governance_family_map(root))
    violations.extend(_run_docs_generate_check(root))

    report: dict[str, Any] = {
        "version": 1,
        "strict": args.strict,
        "ok": len(violations) == 0,
        "violations": violations,
        "inventory_summary": inventory.get("summary", {}),
    }

    out_path = root / str(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path.relative_to(root).as_posix()}")

    if violations:
        for item in violations:
            print(f"DOC-FRESHNESS: {item}")
        return 1 if bool(args.strict) else 0
    print("OK: docs freshness checks passed")
    return 0


def _perf_resolve(root: Path, raw: str) -> Path:
    text = str(raw)
    p = Path(text)
    if text.startswith("/"):
        if p.exists():
            return p
        return root / text.lstrip("/")
    if p.is_absolute():
        return p
    return root / text.lstrip("/")


def _perf_load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json: {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _perf_read_total_ms(path: Path) -> float:
    payload = _perf_load_json(path)
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError(f"timing summary missing: {path}")
    value = summary.get("total_duration_ms")
    if not isinstance(value, (int, float)):
        raise ValueError(f"summary.total_duration_ms missing: {path}")
    return float(value)


def _perf_sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _perf_read_baseline(path: Path) -> tuple[float, float, float]:
    payload = _perf_load_json(path)
    baseline = payload.get("baseline")
    tolerance = payload.get("tolerance")
    if not isinstance(baseline, dict) or not isinstance(tolerance, dict):
        raise ValueError(f"baseline/tolerance mappings required: {path}")
    base_ms = baseline.get("total_duration_ms")
    ratio = tolerance.get("max_regression_ratio")
    absolute = tolerance.get("max_regression_absolute_ms")
    if not isinstance(base_ms, (int, float)):
        raise ValueError(f"baseline.total_duration_ms must be numeric: {path}")
    if not isinstance(ratio, (int, float)):
        raise ValueError(f"tolerance.max_regression_ratio must be numeric: {path}")
    if not isinstance(absolute, (int, float)):
        raise ValueError(f"tolerance.max_regression_absolute_ms must be numeric: {path}")
    return float(base_ms), float(ratio), float(absolute)


def _perf_load_baseline_notes(path: Path) -> dict[str, str]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing baseline notes file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid yaml baseline notes: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"baseline notes payload must be a mapping: {path}")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"baseline notes entries must be a list: {path}")
    out: dict[str, str] = {}
    for idx, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"baseline notes entry[{idx}] must be a mapping: {path}")
        baseline = str(item.get("baseline", "")).strip()
        sha = str(item.get("sha256", "")).strip()
        if not baseline or not sha:
            continue
        out[baseline] = sha
    return out


def _perf_contract_rel(root: Path, path: Path) -> str:
    try:
        return "/" + path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _perf_run(cmd: list[str], *, cwd: Path) -> int:
    cp = subprocess.run(cmd, cwd=cwd, check=False)
    return int(cp.returncode)


def _perf_ensure_generated_file(
    *,
    path: Path,
    regenerate_cmd: list[str],
    cwd: Path,
) -> None:
    if path.exists():
        return
    code = _perf_run(regenerate_cmd, cwd=cwd)
    if code != 0:
        raise ValueError(f"failed to regenerate missing file: {path}")
    if not path.exists():
        raise ValueError(f"missing file: {path}")


def perf_smoke_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run local perf smoke checks for governance/docs timing.")
    ap.add_argument("--mode", choices=("warn", "strict"), default="warn")
    ap.add_argument("--governance-baseline", default="/specs/governance/metrics/governance_timing_baseline.json")
    ap.add_argument("--docs-baseline", default="/specs/governance/metrics/docs_generate_timing_baseline.json")
    ap.add_argument("--governance-profile-baseline", default="/specs/governance/metrics/governance_profile_baseline.json")
    ap.add_argument("--docs-profile-baseline", default="/specs/governance/metrics/docs_generate_profile_baseline.json")
    ap.add_argument("--governance-timing", default="/.artifacts/governance-timing.json")
    ap.add_argument("--docs-timing", default="/.artifacts/docs-generate-timing.json")
    ap.add_argument("--governance-profile", default="/.artifacts/governance-profile.json")
    ap.add_argument("--docs-profile", default="/.artifacts/docs-generate-profile.json")
    ap.add_argument("--baseline-notes", default="/specs/governance/metrics/baseline_update_notes.yaml")
    ap.add_argument("--report-out", default="/.artifacts/perf-smoke-report.json")
    ap.add_argument("--compare-only", action="store_true", help="Skip command execution and compare existing timing files")
    ns = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[3]
    py = root / ".venv/bin/python"
    py_bin = str(py) if py.exists() else "python3"

    governance_timing = _perf_resolve(root, str(ns.governance_timing))
    docs_timing = _perf_resolve(root, str(ns.docs_timing))
    governance_profile = _perf_resolve(root, str(ns.governance_profile))
    docs_profile = _perf_resolve(root, str(ns.docs_profile))
    governance_baseline = _perf_resolve(root, str(ns.governance_baseline))
    docs_baseline = _perf_resolve(root, str(ns.docs_baseline))
    governance_profile_baseline = _perf_resolve(root, str(ns.governance_profile_baseline))
    docs_profile_baseline = _perf_resolve(root, str(ns.docs_profile_baseline))
    baseline_notes = _perf_resolve(root, str(ns.baseline_notes))
    report_out = _perf_resolve(root, str(ns.report_out))

    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    if not bool(ns.compare_only):
        governance_cmd = [
            py_bin,
            "-m",
            "spec_runner.spec_lang_commands",
            "run-governance-specs",
            "--timing-out",
            str(governance_timing),
            "--profile",
            "--profile-out",
            str(governance_profile),
        ]
        code = _perf_run(governance_cmd, cwd=root)
        if code != 0:
            return code
        docs_cmd = [
            py_bin,
            "-m",
            "spec_runner.spec_lang_commands",
            "docs-generate-all",
            "--check",
            "--timing-out",
            str(docs_timing),
            "--profile",
            "--profile-out",
            str(docs_profile),
        ]
        code = _perf_run(docs_cmd, cwd=root)
        if code != 0:
            return code
        _perf_ensure_generated_file(path=governance_timing, regenerate_cmd=governance_cmd, cwd=root)
        _perf_ensure_generated_file(path=governance_profile, regenerate_cmd=governance_cmd, cwd=root)
        _perf_ensure_generated_file(path=docs_timing, regenerate_cmd=docs_cmd, cwd=root)
        _perf_ensure_generated_file(path=docs_profile, regenerate_cmd=docs_cmd, cwd=root)

    for label, timing_path, baseline_path in (
        ("governance_timing", governance_timing, governance_baseline),
        ("docs_generate_timing", docs_timing, docs_baseline),
        ("governance_profile", governance_profile, governance_profile_baseline),
        ("docs_generate_profile", docs_profile, docs_profile_baseline),
    ):
        current = _perf_read_total_ms(timing_path)
        baseline_ms, ratio, absolute = _perf_read_baseline(baseline_path)
        allowed = baseline_ms * (1.0 + ratio) + absolute
        ok = current <= allowed
        row = {
            "id": label,
            "current_total_duration_ms": round(current, 3),
            "baseline_total_duration_ms": round(baseline_ms, 3),
            "max_allowed_duration_ms": round(allowed, 3),
            "max_regression_ratio": ratio,
            "max_regression_absolute_ms": absolute,
            "status": "pass" if ok else "fail",
        }
        checks.append(row)
        if not ok:
            failures.append(
                f"{label}: timing regression ({current:.3f}ms > allowed {allowed:.3f}ms; baseline {baseline_ms:.3f}ms)"
            )

    notes = _perf_load_baseline_notes(baseline_notes)
    for baseline_path in (
        governance_baseline,
        docs_baseline,
        governance_profile_baseline,
        docs_profile_baseline,
    ):
        baseline_key = _perf_contract_rel(root, baseline_path)
        expected_sha = _perf_sha256_hex(baseline_path)
        noted_sha = notes.get(baseline_key, "") or notes.get(baseline_key.lstrip("/"), "")
        ok = noted_sha == expected_sha
        checks.append(
            {
                "id": f"baseline_notes:{baseline_key}",
                "baseline": baseline_key,
                "expected_sha256": expected_sha,
                "noted_sha256": noted_sha,
                "status": "pass" if ok else "fail",
            }
        )
        if not ok:
            failures.append(
                f"baseline notes mismatch for {baseline_key} (expected sha256 {expected_sha})"
            )

    payload = {
        "version": 1,
        "mode": str(ns.mode),
        "status": "pass" if not failures else ("warn" if str(ns.mode) == "warn" else "fail"),
        "checks": checks,
        "errors": failures,
    }
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {report_out.relative_to(root).as_posix() if report_out.is_relative_to(root) else report_out}")
    if failures:
        for msg in failures:
            print(f"WARN: {msg}" if str(ns.mode) == "warn" else f"ERROR: {msg}")
    return 0 if (not failures or str(ns.mode) == "warn") else 1
