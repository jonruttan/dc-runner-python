#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from spec_runner.quality_metrics import objective_scorecard_report_jsonable


def _to_markdown(payload: dict[str, Any]) -> str:
    summary_raw = payload.get("summary")
    summary: dict[str, Any] = summary_raw if isinstance(summary_raw, dict) else {}
    lines = [
        "# Objective Scorecard Report",
        "",
        f"- objective count: {int(summary.get('objective_count', 0))}",
        f"- overall min score: {float(summary.get('overall_min_score', 0.0)):.4f}",
        f"- overall mean score: {float(summary.get('overall_mean_score', 0.0)):.4f}",
        f"- overall status: {str(summary.get('overall_status', 'unknown'))}",
        f"- tripwire hit count: {int(summary.get('tripwire_hit_count', 0))}",
        "",
        "## Objectives",
        "",
        "| id | status | score | primary value |",
        "| --- | --- | ---: | --- |",
    ]
    objectives = payload.get("objectives")
    for row in objectives if isinstance(objectives, list) else []:
        if not isinstance(row, dict):
            continue
        primary_raw = row.get("primary")
        primary: dict[str, Any] = primary_raw if isinstance(primary_raw, dict) else {}
        lines.append(
            f"| {row.get('id', '')} | {row.get('status', '')} | "
            f"{float(row.get('score', 0.0)):.4f} | {primary.get('value_rendered', 'missing')} |"
        )

    tripwires_raw = payload.get("tripwire_hits")
    tripwires = tripwires_raw if isinstance(tripwires_raw, list) else []
    lines.extend(["", "## Tripwire Hits", ""])
    if tripwires:
        lines.extend([
            "| objective | check_id | reason |",
            "| --- | --- | --- |",
        ])
        for hit in tripwires:
            if not isinstance(hit, dict):
                continue
            lines.append(
                f"| {hit.get('objective_id', '')} | {hit.get('check_id', '')} | {hit.get('reason', '')} |"
            )
    else:
        lines.append("- none")

    recos_raw = payload.get("course_correction_recommendations")
    recos = recos_raw if isinstance(recos_raw, list) else []
    lines.extend(["", "## Course Correction", ""])
    if recos:
        for rec in recos:
            lines.append(f"- {rec}")
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def _load_config(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("config payload must be a mapping")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit objective scorecard report as JSON or Markdown.")
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    ap.add_argument("--config", default="", help="Optional YAML/JSON config file path.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    config: dict | None = None
    if str(ns.config).strip():
        config = _load_config(Path(str(ns.config)))

    payload = objective_scorecard_report_jsonable(repo_root, config=config)
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
