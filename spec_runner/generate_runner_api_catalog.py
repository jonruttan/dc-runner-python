#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from spec_runner.docs_generators import (
    parse_generated_block,
    replace_generated_block,
    write_json,
)
from spec_runner.docs_template_engine import render_moustache


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _parse_shell_case_labels(text: str) -> set[str]:
    labels: set[str] = set()
    for line in text.splitlines():
        m = re.match(r"\s{2}([a-z0-9_-]+)\)", line)
        if m:
            labels.add(m.group(1))
    return labels


def _parse_rust_subcommands(text: str) -> set[str]:
    labels: set[str] = set()
    for m in re.finditer(r'"([a-z0-9_-]+)"\s*=>', text):
        labels.add(m.group(1))
    return labels


def _default_semantics(command: str) -> dict[str, Any]:
    group = "reporting"
    if command in {"governance", "normalize-check", "normalize-fix", "lint", "typecheck", "test-core", "test-full"}:
        group = "verification"
    elif command.startswith("docs-") or command.startswith("schema-"):
        group = "docs"
    elif command.endswith("-json") or command.endswith("-md"):
        group = "metrics"
    elif command in {"ci-cleanroom", "ci-gate-summary"}:
        group = "ci"
    return {
        "group": group,
        "summary": f"Runs `{command}` through the canonical runner entrypoint.",
        "details": "Deterministic command dispatch through runners/public/runner_adapter.sh.",
        "defaults": [
            {"name": "impl", "value": "rust", "description": "Default runner implementation lane."},
        ],
        "failure_modes": [
            "Unknown subcommand.",
            "Underlying command returns non-zero status.",
        ],
        "examples": [
            {
                "title": "Direct invocation",
                "command": f"./runners/public/runner_adapter.sh {command}",
                "description": "Execute command with canonical adapter routing.",
            }
        ],
    }


def _build_payload(repo_root: Path) -> dict[str, Any]:
    python_text = (repo_root / "runners/python/runner_adapter.sh").read_text(encoding="utf-8")
    rust_text = (repo_root / "runners/rust/spec_runner_cli/src/main.rs").read_text(encoding="utf-8")
    public_text = (repo_root / "runners/public/runner_adapter.sh").read_text(encoding="utf-8")

    python_cmds = _parse_shell_case_labels(python_text)
    rust_cmds = _parse_rust_subcommands(rust_text)
    public_impls = _parse_shell_case_labels(public_text)

    all_cmds = sorted(python_cmds.union(rust_cmds))
    rows: list[dict[str, Any]] = []
    for cmd in all_cmds:
        semantics = _default_semantics(cmd)
        rows.append(
            {
                "command": cmd,
                "python_supported": cmd in python_cmds,
                "rust_supported": cmd in rust_cmds,
                "parity": cmd in python_cmds and cmd in rust_cmds,
                "summary": semantics["summary"],
                "details": semantics["details"],
                "group": semantics["group"],
                "defaults": semantics["defaults"],
                "failure_modes": semantics["failure_modes"],
                "examples": semantics["examples"],
                "anchor": cmd.replace("_", "-"),
            }
        )

    complete_rows = 0
    for row in rows:
        if (
            str(row.get("summary", "")).strip()
            and isinstance(row.get("defaults"), list)
            and isinstance(row.get("failure_modes"), list)
            and isinstance(row.get("examples"), list)
            and bool(row.get("examples"))
        ):
            complete_rows += 1
    coverage = 0.0 if not rows else (complete_rows / len(rows))

    return {
        "version": 2,
        "summary": {
            "command_count": len(all_cmds),
            "python_command_count": len(python_cmds),
            "rust_command_count": len(rust_cmds),
            "parity_command_count": sum(1 for r in rows if bool(r.get("parity"))),
            "all_commands_parity": all(bool(r.get("parity")) for r in rows),
            "public_impl_modes": sorted(public_impls),
        },
        "quality": {
            "semantics_complete_count": complete_rows,
            "semantics_coverage_ratio": round(coverage, 4),
            "score": round((coverage * 0.6) + ((sum(1 for r in rows if bool(r.get("parity"))) / len(rows)) * 0.4 if rows else 0.0), 4),
        },
        "commands": rows,
    }


def _render_md(payload: dict[str, Any], *, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {"runner": payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate runner API catalog JSON and markdown section.")
    ap.add_argument("--out", default=".artifacts/runner-api-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/91_appendix_runner_api_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload, template_path=repo_root / "docs/book/templates/runner_api_catalog_template.md")
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="runner_api_catalog",
        body=md_block,
    )

    if ns.check:
        if (parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="runner_api_catalog").strip()
                != md_block.strip()):
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if out_path.exists():
            expected_json = json.dumps(payload, indent=2, sort_keys=True).strip()
            if out_path.read_text(encoding="utf-8").strip() != expected_json:
                print(f"{ns.out}: generated content out of date")
                return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
