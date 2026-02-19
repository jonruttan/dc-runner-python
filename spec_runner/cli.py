from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from spec_runner.conformance import report_to_jsonable, run_conformance_cases
from spec_runner.conformance_parity import ParityConfig, build_parity_artifact, run_parity_check
from spec_runner.dispatcher import SpecRunContext
from spec_runner.runtime_context import MiniCapsys, MiniMonkeyPatch
from spec_runner.settings import SETTINGS


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def conformance_runner_main(argv: list[str] | None = None) -> int:
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
    _write_json(Path(str(ns.out)), payload)
    return 0 if all(r.status in {"pass", "skip"} for r in results) else 1


def compare_parity_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run Python/PHP conformance and report normalized parity diffs by case id."
    )
    ap.add_argument(
        "--cases",
        default="specs/conformance/cases",
        help="Path to conformance case docs directory",
    )
    ap.add_argument(
        "--php-runner",
        default="runners/php/conformance_runner.php",
        help="Path to PHP conformance runner script",
    )
    ap.add_argument(
        "--python-runner",
        default="spec_runner.python_conformance_runner",
        help="Python conformance runner module (default) or script path",
    )
    ap.add_argument(
        "--out",
        default="",
        help="Optional path to write JSON parity artifact",
    )
    ap.add_argument(
        "--case-formats",
        default="md",
        help="Comma-separated case formats to load (md,yaml,json). Default: md",
    )
    ap.add_argument(
        "--php-timeout-seconds",
        type=int,
        default=30,
        help="Timeout in seconds for the PHP parity runner subprocess (default: 30)",
    )
    ap.add_argument(
        "--python-timeout-seconds",
        type=int,
        default=30,
        help="Timeout in seconds for the Python parity runner subprocess (default: 30)",
    )
    ns = ap.parse_args(argv)
    out_path = Path(str(ns.out)).resolve() if str(ns.out).strip() else None

    if shutil.which("php") is None:
        msg = "php executable not found in PATH"
        if out_path is not None:
            _write_json(out_path, build_parity_artifact([msg]))
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    case_formats = {x.strip() for x in str(ns.case_formats).split(",") if x.strip()}
    if not case_formats:
        msg = "--case-formats requires at least one format"
        if out_path is not None:
            _write_json(out_path, build_parity_artifact([msg]))
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2

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
    except RuntimeError as err:
        if out_path is not None:
            _write_json(out_path, build_parity_artifact([str(err)]))
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    if out_path is not None:
        _write_json(out_path, build_parity_artifact(errs))
    if errs:
        print("ERROR: conformance parity check failed", file=sys.stderr)
        for msg in errs:
            print(f"- {msg}", file=sys.stderr)
        return 1

    print(f"OK: conformance parity matched for {cfg.cases_dir}")
    return 0
