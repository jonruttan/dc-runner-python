from __future__ import annotations

import argparse
from pathlib import Path

from spec_runner.settings import SETTINGS
from spec_runner.spec_lang_hygiene import SpecLangIssue, lint_cases


def _render_issues(issues: list[SpecLangIssue]) -> int:
    if not issues:
        print("OK: spec-lang lint passed")
        return 0
    for issue in issues:
        print(issue.render())
    print(f"FAIL: spec-lang lint found {len(issues)} issue(s)")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Lint spec-lang assertion expressions and hooks in executable contract-spec cases.",
    )
    ap.add_argument(
        "--cases",
        default="specs",
        help="Path to case docs directory or case file",
    )
    ap.add_argument(
        "--case-file-pattern",
        default=SETTINGS.case.default_file_pattern,
        help="Glob pattern for markdown case files when --cases points to a directory",
    )
    ap.add_argument(
        "--case-formats",
        default="md",
        help="Comma-separated case formats to load (md,yaml,json). Default: md",
    )
    ns = ap.parse_args(argv)

    case_pattern = str(ns.case_file_pattern).strip()
    if not case_pattern:
        print("ERROR: --case-file-pattern requires a non-empty value")
        return 2

    case_formats = {x.strip() for x in str(ns.case_formats).split(",") if x.strip()}
    if not case_formats:
        print("ERROR: --case-formats requires at least one format")
        return 2

    cases_path = Path(str(ns.cases))
    if not cases_path.exists():
        print(f"ERROR: cases path does not exist: {cases_path}")
        return 2

    return _render_issues(
        lint_cases(
            cases_path,
            case_file_pattern=case_pattern,
            case_formats=case_formats,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
