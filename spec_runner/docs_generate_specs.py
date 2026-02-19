#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import json
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from spec_runner.dispatcher import SpecRunContext, iter_cases, run_case
from spec_runner.runtime_context import MiniCapsys, MiniMonkeyPatch
from spec_runner.settings import case_file_name
from spec_runner.components.profiler import RunProfiler, profile_config_from_args
from spec_runner.virtual_paths import resolve_contract_path


def _resolve_out(repo_root: Path, raw: str, *, field: str) -> Path:
    try:
        return resolve_contract_path(repo_root, raw, field=field)
    except Exception:
        return repo_root / str(raw).lstrip("/")


def _surface_id(case_test: dict[str, Any]) -> str:
    harness = case_test.get("harness") if isinstance(case_test, dict) else None
    if not isinstance(harness, dict):
        return ""
    docs_generate = harness.get("docs_generate")
    if not isinstance(docs_generate, dict):
        return ""
    return str(docs_generate.get("surface_id", "")).strip()


def _render_summary(payload: dict[str, Any]) -> str:
    lines = [
        "# Docs Generate Specs Summary",
        "",
        f"- status: {payload.get('status', 'fail')}",
        f"- case_count: {int(payload.get('summary', {}).get('case_count', 0))}",
        f"- passed_count: {int(payload.get('summary', {}).get('passed_count', 0))}",
        f"- failed_count: {int(payload.get('summary', {}).get('failed_count', 0))}",
        "",
        "| case_id | surface_id | status |",
        "|---|---|---|",
    ]
    for row in payload.get("cases") or []:
        lines.append(
            f"| `{row.get('case_id', '')}` | `{row.get('surface_id', '')}` | `{row.get('status', 'fail')}` |"
        )
    lines.append("")
    errors = payload.get("errors") or []
    if errors:
        lines += ["## Errors", ""]
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run docs.generate executable specs.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    ap.add_argument("--surface", default="", help="Optional docs surface_id filter")
    ap.add_argument("--cases", default="specs/impl/docs_generate/cases")
    ap.add_argument("--jobs", type=int, default=0, help="Parallel jobs for independent docs surfaces (0=auto)")
    ap.add_argument("--report-out", default=".artifacts/docs-generator-report.json")
    ap.add_argument("--summary-out", default=".artifacts/docs-generator-summary.md")
    ap.add_argument("--timing-out", default=".artifacts/docs-generate-timing.json")
    ap.add_argument("--profile", action="store_true", help="Emit per-case harness timing profile JSON")
    ap.add_argument("--profile-out", default=".artifacts/docs-generate-profile.json")
    ap.add_argument("--profile-level", default="", help="off|basic|detailed|debug (default off)")
    ap.add_argument("--profile-summary-out", default="", help="Run trace summary markdown output path")
    ap.add_argument("--profile-heartbeat-ms", type=int, default=0, help="Profiler heartbeat interval (ms)")
    ap.add_argument("--profile-stall-threshold-ms", type=int, default=0, help="Profiler stall threshold (ms)")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    profiler_cfg = profile_config_from_args(
        profile_level=str(ns.profile_level).strip() or None,
        profile_out=None,
        profile_summary_out=str(ns.profile_summary_out).strip() or None,
        profile_heartbeat_ms=ns.profile_heartbeat_ms if int(ns.profile_heartbeat_ms or 0) > 0 else None,
        profile_stall_threshold_ms=ns.profile_stall_threshold_ms if int(ns.profile_stall_threshold_ms or 0) > 0 else None,
        runner_impl=str(os.environ.get("SPEC_RUNNER_IMPL", "python")),
        command="docs-generate-specs",
        args=list(argv or []),
        env=dict(os.environ),
    )
    profiler = RunProfiler(profiler_cfg)
    mode_value = "check" if ns.check else "write"
    case_dir = _resolve_out(repo_root, str(ns.cases), field="docs_generate_specs.cases")
    if not case_dir.exists():
        print(f"missing docs generate cases path: {ns.cases}")
        return 1

    selected = []
    for case in iter_cases(case_dir, file_pattern=case_file_name("*")):
        if str(case.test.get("type", "")).strip() != "docs.generate":
            continue
        sid = _surface_id(case.test)
        if str(ns.surface).strip() and sid != str(ns.surface).strip():
            continue
        selected.append((case, sid))

    errors: list[str] = []
    if str(ns.surface).strip() and not selected:
        errors.append(f"unknown surface_id: {str(ns.surface).strip()}")

    rows: list[dict[str, Any]] = []
    timing_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    env = dict(os.environ)
    env["SPEC_DOCS_GENERATE_MODE"] = mode_value

    try:
        with TemporaryDirectory(prefix="spec-runner-docs-generate-") as td:
            td_path = Path(td)
            workers_used = 1

            def _run_one(task: tuple[int, Any, str]) -> tuple[int, dict[str, Any], float, str | None, list[dict[str, Any]]]:
                idx, case, sid = task
                case_id = str(case.test.get("id", "")).strip() or "<unknown>"
                case_tmp = td_path / f"case_{idx}"
                case_tmp.mkdir(parents=True, exist_ok=True)
                ctx = SpecRunContext(
                    tmp_path=case_tmp,
                    patcher=MiniMonkeyPatch(),
                    capture=MiniCapsys(),
                    env=env,
                    profile_enabled=bool(ns.profile),
                    profiler=profiler if profiler.cfg.enabled else None,
                )
                case_started = time.perf_counter()
                try:
                    with (
                        profiler.span(
                            name="check.execute",
                            kind="check",
                            phase="docs.generate.case",
                            attrs={"case_id": case_id, "surface_id": sid},
                        )
                        if profiler.cfg.enabled
                        else contextlib.nullcontext()
                    ):
                        run_case(case, ctx=ctx)
                    elapsed_ms = (time.perf_counter() - case_started) * 1000.0
                    return idx, {"case_id": case_id, "surface_id": sid, "status": "pass"}, elapsed_ms, None, list(ctx.profile_rows)
                except BaseException as exc:  # noqa: BLE001
                    elapsed_ms = (time.perf_counter() - case_started) * 1000.0
                    return (
                        idx,
                        {"case_id": case_id, "surface_id": sid, "status": "fail"},
                        elapsed_ms,
                        f"{case_id}: {exc}",
                        list(ctx.profile_rows),
                    )

            indexed = [(idx, case, sid) for idx, (case, sid) in enumerate(selected)]
            if len(indexed) <= 1:
                for task in indexed:
                    _idx, row, elapsed_ms, err, case_profile_rows = _run_one(task)
                    rows.append(row)
                    timing_rows.append(
                        {
                            "index": int(_idx),
                            "case_id": str(row.get("case_id", "")),
                            "surface_id": str(row.get("surface_id", "")),
                            "duration_ms": round(float(elapsed_ms), 3),
                            "status": str(row.get("status", "fail")),
                        }
                    )
                    profile_rows.extend(case_profile_rows)
                    if err:
                        errors.append(err)
            else:
                auto_workers = max(1, os.cpu_count() or 1)
                requested = int(ns.jobs)
                if requested <= 0:
                    max_workers = min(auto_workers, len(indexed))
                else:
                    max_workers = min(max(1, requested), len(indexed))
                workers_used = max_workers
                results: list[tuple[int, dict[str, Any], float, str | None, list[dict[str, Any]]]] = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for result in executor.map(_run_one, indexed):
                        results.append(result)
                for _idx, row, elapsed_ms, err, case_profile_rows in sorted(results, key=lambda x: x[0]):
                    rows.append(row)
                    timing_rows.append(
                        {
                            "index": int(_idx),
                            "case_id": str(row.get("case_id", "")),
                            "surface_id": str(row.get("surface_id", "")),
                            "duration_ms": round(float(elapsed_ms), 3),
                            "status": str(row.get("status", "fail")),
                        }
                    )
                    profile_rows.extend(case_profile_rows)
                    if err:
                        errors.append(err)
    finally:
        profile_out_raw = str(os.environ.get("SPEC_RUNNER_PROFILE_OUT", "")).strip() or "/.artifacts/run-trace.json"
        profile_summary_out_raw = str(ns.profile_summary_out).strip() or str(
            os.environ.get("SPEC_RUNNER_PROFILE_SUMMARY_OUT", "")
        ).strip() or "/.artifacts/run-trace-summary.md"
        profile_out_path = _resolve_out(repo_root, profile_out_raw, field="docs_generate_specs.profile_trace_out")
        profile_summary_out_path = _resolve_out(
            repo_root,
            profile_summary_out_raw,
            field="docs_generate_specs.profile_trace_summary_out",
        )
        profiler.close(
            status="fail" if errors else "pass",
            out_path=profile_out_path,
            summary_out_path=profile_summary_out_path,
            exit_code=1 if errors else 0,
        )

    passed = sum(1 for x in rows if x["status"] == "pass")
    failed = len(rows) - passed
    payload = {
        "version": 1,
        "status": "pass" if not errors and failed == 0 else "fail",
        "summary": {
            "case_count": len(rows),
            "passed_count": passed,
            "failed_count": failed,
        },
        "cases": rows,
        "errors": errors,
    }

    report_path = _resolve_out(repo_root, str(ns.report_out), field="docs_generate_specs.report_out")
    summary_path = _resolve_out(repo_root, str(ns.summary_out), field="docs_generate_specs.summary_out")
    timing_path = _resolve_out(repo_root, str(ns.timing_out), field="docs_generate_specs.timing_out")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    timing_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(_render_summary(payload), encoding="utf-8")
    total_ms = (time.perf_counter() - started) * 1000.0
    timing_payload = {
        "version": 1,
        "status": payload["status"],
        "summary": {
            "case_count": len(rows),
            "failed_count": int(failed),
            "workers_used": int(workers_used),
            "total_duration_ms": round(float(total_ms), 3),
        },
        "cases": timing_rows,
    }
    timing_path.write_text(json.dumps(timing_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if ns.profile:
        sorted_profile = sorted(profile_rows, key=lambda row: float(row.get("duration_ms", 0.0)), reverse=True)
        profile_payload = {
            "version": 1,
            "status": payload["status"],
            "summary": {
                "case_count": len(rows),
                "record_count": len(sorted_profile),
                "total_duration_ms": round(float(total_ms), 3),
            },
            "top_slowest": sorted_profile[:20],
            "records": sorted_profile,
        }
        profile_path = _resolve_out(repo_root, str(ns.profile_out), field="docs_generate_specs.profile_out")
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(json.dumps(profile_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {ns.report_out}")
    print(f"wrote {ns.summary_out}")
    print(f"wrote {ns.timing_out}")
    if ns.profile:
        print(f"wrote {ns.profile_out}")
    if errors:
        for err in errors:
            print(err)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
