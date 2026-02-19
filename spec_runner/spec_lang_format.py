from __future__ import annotations

import argparse
from pathlib import Path

from spec_runner.settings import SETTINGS
from spec_runner.spec_lang_hygiene import format_file, iter_case_files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Format spec-lang assertion expressions in yaml contract-spec blocks.",
    )
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if files need formatting")
    mode.add_argument("--write", action="store_true", help="rewrite files in place")
    ap.add_argument(
        "--pattern",
        default=SETTINGS.case.default_file_pattern,
        help="Case doc filename glob (default from settings)",
    )
    ap.add_argument(
        "paths",
        nargs="*",
        default=["specs"],
        help="Files or directories to process",
    )
    ns = ap.parse_args(argv)

    files = iter_case_files([Path(x) for x in ns.paths], pattern=str(ns.pattern))
    changed: list[Path] = []
    for p in files:
        updated, is_changed = format_file(p)
        if is_changed:
            changed.append(p)
            if ns.write:
                p.write_text(updated, encoding="utf-8")

    if ns.check:
        if changed:
            for p in changed:
                print(f"NEEDS_FORMAT: {p.as_posix()}")
            return 1
        print("OK: spec-lang formatting is canonical")
        return 0

    print(f"formatted {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
