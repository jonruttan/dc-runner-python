#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from spec_runner.quality_metrics import spec_lang_adoption_report_jsonable


def _to_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Spec-Lang Adoption Report",
        "",
        f"- total cases: {int(summary.get('total_cases', 0))}",
        f"- overall logic self-contained ratio: {float(summary.get('overall_logic_self_contained_ratio', 0.0)):.4f}",
        f"- native logic escape case ratio: {float(summary.get('native_logic_escape_case_ratio', 0.0)):.4f}",
        f"- governance symbol resolution ratio: {float(summary.get('governance_symbol_resolution_ratio', 0.0)):.4f}",
        f"- library public surface ratio: {float(summary.get('library_public_surface_ratio', 0.0)):.4f}",
        f"- unit opt-out count: {int(summary.get('unit_opt_out_count', 0))}",
        "",
        "## Segment Summary",
        "",
        "| segment | case_count | logic_self_contained_ratio | native_logic_escape_case_ratio |",
        "| --- | ---: | ---: | ---: |",
    ]
    for seg, row in sorted((payload.get("segments") or {}).items()):
        lines.append(
            f"| {seg} | {int(row.get('case_count', 0))} | "
            f"{float(row.get('mean_logic_self_contained_ratio', 0.0)):.4f} | "
            f"{float(row.get('native_logic_escape_case_ratio', 0.0)):.4f} |"
        )
    return "\n".join(lines) + "\n"


def _load_config(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("config payload must be a mapping")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit spec-lang adoption metric report as JSON or Markdown.")
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    ap.add_argument("--config", default="", help="Optional YAML/JSON config file path.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    config: dict | None = None
    if str(ns.config).strip():
        config = _load_config(Path(str(ns.config)))

    payload = spec_lang_adoption_report_jsonable(repo_root, config=config)
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
