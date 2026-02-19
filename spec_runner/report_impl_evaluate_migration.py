#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from spec_runner.doc_parser import iter_spec_doc_tests
from spec_runner.quality_metrics import _collect_leaf_ops


def _classify(*, eval_count: int, total_count: int, has_library_paths: bool) -> str:
    if total_count <= 0 or eval_count >= total_count:
        return "already_evaluate_primary"
    if has_library_paths:
        return "convertible_now_library_backed"
    return "convertible_now_simple"


def report(cases_dir: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    classes: Counter[str] = Counter()
    op_totals: Counter[str] = Counter()

    case_pairs: list[Any] = []
    if cases_dir.is_file():
        case_pairs = list(iter_spec_doc_tests(cases_dir.parent, file_pattern=cases_dir.name))
    else:
        for spec_file in sorted(cases_dir.rglob("*.spec.md")):
            if not spec_file.is_file():
                continue
            case_pairs.extend(iter_spec_doc_tests(spec_file.parent, file_pattern=spec_file.name))

    for case in case_pairs:
        t = case.test
        case_id = str(t.get("id", "")).strip()
        case_type = str(t.get("type", "")).strip()
        ops = _collect_leaf_ops(t.get("contract", []) or [])
        counts = Counter(ops)
        total = len(ops)
        eval_count = counts.get("evaluate", 0)
        ratio = float(eval_count) / float(total) if total else 1.0
        harness = t.get("harness")
        has_library_paths = False
        if isinstance(harness, dict):
            spec_lang = harness.get("spec_lang")
            if isinstance(spec_lang, dict):
                lib_paths = spec_lang.get("includes")
                has_library_paths = isinstance(lib_paths, list) and any(
                    isinstance(x, str) and x.strip() for x in lib_paths
                )
        classification = _classify(
            eval_count=eval_count,
            total_count=total,
            has_library_paths=has_library_paths,
        )
        classes[classification] += 1
        op_totals.update(counts)
        rows.append(
            {
                "id": case_id,
                "type": case_type,
                "file": str(case.doc_path).replace("\\", "/"),
                "total_leaf_ops": total,
                "evaluate_leaf_ops": eval_count,
                "evaluate_ratio": ratio,
                "has_library_paths": has_library_paths,
                "leaf_ops": dict(sorted(counts.items())),
                "classification": classification,
            }
        )

    rows.sort(key=lambda r: (r["classification"], r["file"], r["id"]))
    total_leaf_ops = sum(float(r["total_leaf_ops"]) for r in rows)
    evaluate_leaf_ops = sum(float(r["evaluate_leaf_ops"]) for r in rows)
    ratio = float(evaluate_leaf_ops) / float(total_leaf_ops) if total_leaf_ops > 0 else 1.0
    blocked = int(classes.get("blocked_subject_shape_gap", 0))
    return {
        "version": 1,
        "summary": {
            "total_cases": len(rows),
            "mean_logic_self_contained_ratio": ratio,
            "classification_counts": dict(sorted(classes.items())),
            "leaf_op_totals": dict(sorted(op_totals.items())),
            "blocked_subject_shape_gap_count": blocked,
        },
        "cases": rows,
    }


def _to_md(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    lines = [
        "# Impl Evaluate Migration",
        "",
        f"- total_cases: `{summary.get('total_cases', 0)}`",
        f"- mean_logic_self_contained_ratio: `{summary.get('mean_logic_self_contained_ratio', 0.0):.6f}`",
        f"- blocked_subject_shape_gap_count: `{summary.get('blocked_subject_shape_gap_count', 0)}`",
        "",
        "## Classification Counts",
    ]
    for key, value in sorted((summary.get("classification_counts") or {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Leaf Op Totals")
    for key, value in sorted((summary.get("leaf_op_totals") or {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Non Evaluate-Primary Cases")
    pending = [r for r in payload.get("cases", []) if r.get("classification") != "already_evaluate_primary"]
    if not pending:
        lines.append("- none")
    else:
        for row in pending:
            lines.append(
                "- "
                + f"`{row.get('id','')}` | `{row.get('type','')}` | "
                + f"`{row.get('evaluate_ratio', 0.0):.3f}` | `{row.get('classification','')}` | `{row.get('file','')}`"
            )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report impl evaluate migration status.")
    parser.add_argument("--cases", default="specs/impl", help="Impl cases directory")
    parser.add_argument(
        "--out-json",
        default=".artifacts/impl-evaluate-migration.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--out-md",
        default=".artifacts/impl-evaluate-migration-summary.md",
        help="Output Markdown summary path",
    )
    args = parser.parse_args(argv)
    payload = report(Path(args.cases))
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_to_md(payload), encoding="utf-8")
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
