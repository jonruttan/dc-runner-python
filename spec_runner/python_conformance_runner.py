#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from spec_runner.conformance import report_to_jsonable, run_conformance_cases
from spec_runner.dispatcher import SpecRunContext
from spec_runner.runtime_context import MiniCapsys, MiniMonkeyPatch
from spec_runner.settings import SETTINGS


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run conformance cases with Python runner and emit normalized report JSON."
    )
    ap.add_argument("--cases", required=True, help="Path to conformance case docs directory or case file")
    ap.add_argument("--out", required=True, help="Path to write JSON report")
    ap.add_argument(
        "--case-file-pattern",
        default=SETTINGS.case.default_file_pattern,
        help="Glob pattern for case files when --cases points to a directory",
    )
    ap.add_argument(
        "--case-formats",
        default="md",
        help="Comma-separated case formats to load (md,yaml,json). Default: md",
    )
    ns = ap.parse_args(argv)

    case_pattern = str(ns.case_file_pattern).strip()
    if not case_pattern:
        print("ERROR: --case-file-pattern requires a non-empty value", file=sys.stderr)
        return 2
    case_formats = {x.strip() for x in str(ns.case_formats).split(",") if x.strip()}
    if not case_formats:
        print("ERROR: --case-formats requires at least one format", file=sys.stderr)
        return 2

    cases_path = Path(str(ns.cases))
    if not cases_path.exists():
        print(f"ERROR: cases path does not exist: {cases_path}", file=sys.stderr)
        return 2

    with TemporaryDirectory(prefix="spec-runner-python-") as td:
        tmp_path = Path(td)
        patcher = MiniMonkeyPatch()
        capture = MiniCapsys()
        ctx = SpecRunContext(tmp_path=tmp_path, patcher=patcher, capture=capture)
        with capture.capture():
            try:
                results = run_conformance_cases(
                    cases_path,
                    ctx=ctx,
                    implementation="python",
                    case_file_pattern=case_pattern,
                    case_formats=case_formats,
                )
            except BaseException as e:  # noqa: BLE001
                print(f"ERROR: {e}", file=sys.stderr)
                return 1

    payload = report_to_jsonable(results)
    _write_report(Path(str(ns.out)), payload)
    return 0 if all(r.status in {"pass", "skip"} for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
