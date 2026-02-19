#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from spec_runner.review_snapshot_validate import (
    parse_classification_labels,
    parse_spec_candidates,
    validate_review_snapshot,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_section(md: str, heading: str) -> str:
    lines = md.splitlines()
    needle = f"## {heading}"
    start = None
    for i, line in enumerate(lines):
        if line.strip() == needle:
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def _write_pending(
    out_path: Path,
    *,
    title: str,
    source: Path,
    candidates: list[dict[str, Any]],
    classifications: dict[str, str],
) -> None:
    today = dt.date.today().isoformat()
    lines: list[str] = []
    lines.append("---")
    lines.append(f"id: CK-REVIEW-{today.replace('-', '')}")
    lines.append(f"title: {title}")
    lines.append("priority: P1")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Source snapshot: `{source.as_posix()}`")
    lines.append("")
    lines.append("## Canonical Candidates")
    lines.append("")

    for candidate in candidates:
        cid = str(candidate.get("id", "")).strip()
        lines.append(f"### {cid}")
        lines.append("")
        lines.append(f"- title: {candidate['title']}")
        lines.append(f"- type: `{candidate['type']}`")
        lines.append(f"- class: `{candidate['class']}`")
        lines.append(f"- target_area: `{candidate['target_area']}`")
        lines.append(f"- risk: `{candidate['risk']}`")
        lines.append(f"- classification: `{classifications.get(cid, 'unclassified')}`")
        lines.append("- acceptance_criteria:")
        for item in candidate.get("acceptance_criteria", []):
            lines.append(f"  - {item}")
        lines.append("- affected_paths:")
        for item in candidate.get("affected_paths", []):
            lines.append(f"  - `{item}`")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Extract canonical YAML review candidates from docs/reviews snapshots into "
            "specs/governance/pending artifacts."
        ),
    )
    ap.add_argument("snapshot", help="Path to review snapshot markdown")
    ap.add_argument(
        "--out",
        default="",
        help="Output pending markdown path (default: specs/governance/pending/<snapshot-stem>-pending.md)",
    )
    ns = ap.parse_args(argv)

    src = Path(ns.snapshot)
    if not src.exists() or not src.is_file():
        print(f"ERROR: snapshot not found: {src}")
        return 2

    violations = validate_review_snapshot(src)
    if violations:
        for line in violations:
            print(f"ERROR: {line}")
        return 1

    md = _read(src)
    candidates_section = _extract_section(md, "Spec Candidates (YAML)")
    labels_section = _extract_section(md, "Classification Labels")

    candidates, parse_errors = parse_spec_candidates(candidates_section)
    if parse_errors:
        for line in parse_errors:
            print(f"ERROR: {src.as_posix()}: {line}")
        return 1

    classifications = parse_classification_labels(labels_section)

    out_path = Path(ns.out) if ns.out else Path("specs/governance/pending") / f"{src.stem}-pending.md"
    _write_pending(
        out_path,
        title="Review-Derived Spec Candidates",
        source=src,
        candidates=candidates,
        classifications=classifications,
    )

    print(f"wrote {out_path.as_posix()} (candidates={len(candidates)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
