#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from spec_runner.quality_metrics import python_dependency_report_jsonable


def _to_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Python Dependency Report",
        "",
        f"- total files: {int(summary.get('total_files', 0))}",
        f"- non-python lane python exec count: {int(summary.get('non_python_lane_python_exec_count', 0))}",
        f"- transitive adapter python exec count: {int(summary.get('transitive_adapter_python_exec_count', 0))}",
        f"- default lane python free ratio: {float(summary.get('default_lane_python_free_ratio', 0.0)):.4f}",
        f"- python usage scope violation count: {int(summary.get('python_usage_scope_violation_count', 0))}",
        "",
        "## Evidence (Static Hits)",
        "",
    ]
    static_hits = (payload.get("evidence") or {}).get("static_hits") or []
    if static_hits:
        lines.extend([
            "| kind | file | token | segment |",
            "| --- | --- | --- | --- |",
        ])
        for hit in static_hits:
            if not isinstance(hit, dict):
                continue
            lines.append(
                f"| {hit.get('kind', '')} | {hit.get('file', '')} | {hit.get('token', '')} | {hit.get('segment', '')} |"
            )
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
    ap = argparse.ArgumentParser(description="Emit python dependency metric report as JSON or Markdown.")
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    ap.add_argument("--config", default="", help="Optional YAML/JSON config file path.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    config: dict | None = None
    if str(ns.config).strip():
        config = _load_config(Path(str(ns.config)))

    payload = python_dependency_report_jsonable(repo_root, config=config)
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
