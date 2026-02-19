#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from spec_runner.spec_portability import spec_portability_report_jsonable


def _to_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Spec Portability Report",
        "",
        f"- total cases: {int(summary.get('total_cases', 0))}",
        (
            "- overall self-contained ratio: "
            f"{float(summary.get('overall_self_contained_ratio', 0.0)):.4f}"
        ),
        (
            "- overall implementation-reliance ratio: "
            f"{float(summary.get('overall_implementation_reliance_ratio', 0.0)):.4f}"
        ),
        (
            "- overall logic self-contained ratio: "
            f"{float(summary.get('overall_logic_self_contained_ratio', 0.0)):.4f}"
        ),
        (
            "- overall execution portability ratio: "
            f"{float(summary.get('overall_execution_portability_ratio', 0.0)):.4f}"
        ),
        "",
        "## Segment Summary",
        "",
        "| segment | case_count | self_contained_ratio | implementation_reliance_ratio | logic_self_contained_ratio | execution_portability_ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    segments = payload.get("segments") or {}
    for segment in sorted(segments):
        row = segments.get(segment) or {}
        lines.append(
            "| "
            f"{segment} | {int(row.get('case_count', 0))} | "
            f"{float(row.get('mean_self_contained_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_implementation_reliance_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_logic_self_contained_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_execution_portability_ratio', 0.0)):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Worst Cases",
            "",
            "| id | type | segment | self_contained_ratio | file | reasons |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )

    worst = payload.get("worst_cases") or []
    if not worst:
        lines.append("| - | - | - | 0.0000 | - | none |")
    for row in worst:
        reasons = ", ".join(str(x) for x in (row.get("reasons") or [])) or "none"
        reasons = reasons.replace("|", "\\|")
        lines.append(
            "| "
            f"{row.get('id', '')} | {row.get('type', '')} | {row.get('segment', '')} | "
            f"{float(row.get('self_contained_ratio', 0.0)):.4f} | {row.get('file', '')} | {reasons} |"
        )

    errors = payload.get("errors") or []
    if errors:
        lines.extend(["", "## Errors", ""])
        for err in errors:
            lines.append(f"- {err}")

    return "\n".join(lines) + "\n"


def _load_config(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("config payload must be a mapping")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Emit spec self-containment/implementation-reliance report as JSON or Markdown."
    )
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    ap.add_argument("--top-n", type=int, default=0, help="Override number of worst cases to include.")
    ap.add_argument("--config", default="", help="Optional YAML/JSON config file path.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]

    config: dict[str, Any] | None = None
    if str(ns.config).strip():
        config = _load_config(Path(str(ns.config)))
    if ns.top_n > 0:
        if config is None:
            config = {}
        report_raw = config.get("report")
        report = dict(report_raw) if isinstance(report_raw, dict) else {}
        report["top_n"] = int(ns.top_n)
        config["report"] = report

    payload = spec_portability_report_jsonable(repo_root, config=config)
    raw = _to_markdown(payload) if ns.format == "md" else json.dumps(payload, indent=2, sort_keys=True) + "\n"

    if ns.out:
        out = Path(ns.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(raw, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
