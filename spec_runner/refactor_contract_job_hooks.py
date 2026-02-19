#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FILES = [
    "specs/impl/rust/jobs/script_jobs.spec.md",
    "specs/impl/rust/jobs/report_jobs.spec.md",
]
FENCE_RE = re.compile(r"```yaml contract-spec\n(.*?)\n```", re.DOTALL)


def _load_yaml(payload: str) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(payload)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False).rstrip("\n")


def _has_dispatch(exprs: Any, job_name: str) -> bool:
    if not isinstance(exprs, list):
        return False
    for expr in exprs:
        if not isinstance(expr, dict):
            continue
        dispatch = expr.get("ops.job.dispatch")
        if not isinstance(dispatch, list) or not dispatch:
            continue
        if str(dispatch[0]).strip() == job_name:
            return True
    return False


def _ensure_job_entry(
    *,
    jobs: dict[str, Any],
    name: str,
    case_id: str,
    suffix: str,
) -> bool:
    expected = {
        "helper": "helper.report.emit",
        "mode": "report",
        "inputs": {
            "out": f".artifacts/job-hooks/{case_id}.{suffix}.json",
            "format": "json",
            "report_name": f"{case_id}.{suffix}",
        },
    }
    current = jobs.get(name)
    if current == expected:
        return False
    jobs[name] = expected
    return True


def _migrate_case(case: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    if str(case.get("type", "")).strip() != "contract.job":
        return case, False

    case_id = str(case.get("id", "")).strip()
    if not case_id:
        return case, False

    harness = case.get("harness")
    if not isinstance(harness, dict):
        return case, False
    jobs = harness.get("jobs")
    if not isinstance(jobs, dict):
        return case, False

    if _ensure_job_entry(jobs=jobs, name="on_fail", case_id=case_id, suffix="fail"):
        changed = True
    if _ensure_job_entry(jobs=jobs, name="on_complete", case_id=case_id, suffix="complete"):
        changed = True

    legacy_bool_on = harness.get(True)
    on_hooks = harness.get("on")
    harness_when = harness.get("when")
    case_when = case.get("when")
    when_hooks = case_when if isinstance(case_when, dict) else None
    if isinstance(legacy_bool_on, dict):
        if not isinstance(when_hooks, dict) and not isinstance(on_hooks, dict) and not isinstance(harness_when, dict):
            when_hooks = legacy_bool_on
            case["when"] = when_hooks
            changed = True
        harness.pop(True, None)
        changed = True
    if isinstance(on_hooks, dict):
        if not isinstance(when_hooks, dict):
            case["when"] = on_hooks
            when_hooks = on_hooks
            changed = True
        harness.pop("on", None)
        changed = True
    if isinstance(harness_when, dict):
        if not isinstance(when_hooks, dict):
            case["when"] = harness_when
            when_hooks = harness_when
            changed = True
        harness.pop("when", None)
        changed = True
    if not isinstance(when_hooks, dict):
        when_hooks = {}
        case["when"] = when_hooks
        changed = True

    fail_exprs = when_hooks.get("fail")
    if not _has_dispatch(fail_exprs, "on_fail"):
        when_hooks["fail"] = [{"ops.job.dispatch": ["on_fail"]}]
        changed = True

    complete_exprs = when_hooks.get("complete")
    if not _has_dispatch(complete_exprs, "on_complete"):
        when_hooks["complete"] = [{"ops.job.dispatch": ["on_complete"]}]
        changed = True

    return case, changed


def migrate_file(path: Path, write: bool) -> bool:
    raw = path.read_text(encoding="utf-8")
    changed_any = False

    def repl(m: re.Match[str]) -> str:
        nonlocal changed_any
        payload = m.group(1)
        case = _load_yaml(payload)
        if case is None:
            return m.group(0)
        migrated, changed = _migrate_case(case)
        if not changed:
            return m.group(0)
        changed_any = True
        return "```yaml contract-spec\n" + _dump_yaml(migrated) + "\n```"

    updated = FENCE_RE.sub(repl, raw)
    if changed_any and write:
        path.write_text(updated, encoding="utf-8")
    return changed_any


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", default=DEFAULT_FILES)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    ns = ap.parse_args()
    if ns.check == ns.write:
        ap.error("choose exactly one of --check or --write")

    files: list[Path] = []
    for p in ns.paths:
        target = Path(p)
        if not target.is_absolute():
            target = (ROOT / p).resolve()
        if target.is_file():
            files.append(target)

    changed_files: list[Path] = []
    for f in files:
        if migrate_file(f, write=ns.write):
            changed_files.append(f)

    if ns.check:
        if changed_files:
            for f in changed_files:
                print(f"NEEDS_REFACTOR: {f.relative_to(ROOT).as_posix()}")
            return 1
        print("OK: contract.job hook refactor already applied")
        return 0
    print(f"OK: rewrote {len(changed_files)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
