#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from spec_runner.schema_registry import compile_registry


BEGIN_MARKER = "<!-- BEGIN GENERATED: SCHEMA_REGISTRY_V1 -->"
END_MARKER = "<!-- END GENERATED: SCHEMA_REGISTRY_V1 -->"


def _generated_section(compiled: dict) -> str:
    top = compiled.get("top_level_fields") or {}
    type_profiles = compiled.get("type_profiles") or {}
    lines: list[str] = [
        BEGIN_MARKER,
        "",
        "## Generated Registry Snapshot",
        "",
        "This section is generated from `specs/schema/registry/v1/*.yaml`.",
        "",
        f"- profile_count: {int(compiled.get('profile_count', 0))}",
        f"- top_level_fields: {len(top)}",
        f"- type_profiles: {len(type_profiles)}",
        "",
        "### Top-Level Keys",
        "",
        "| key | type | required | since |",
        "|---|---|---|---|",
    ]
    for key, meta in sorted(top.items()):
        lines.append(
            f"| `{key}` | `{meta.get('type', 'any')}` | `{str(bool(meta.get('required', False))).lower()}` | `{meta.get('since', 'v1')}` |"
        )
    lines += ["", "### Type Profiles", "", "| type | required keys | extra keys |", "|---|---|---|"]
    for ctype, prof in sorted(type_profiles.items()):
        req = ", ".join(f"`{x}`" for x in prof.get("required_top_level") or []) or "-"
        extra = ", ".join(f"`{x}`" for x in prof.get("allowed_top_level_extra") or []) or "-"
        lines.append(f"| `{ctype}` | {req} | {extra} |")
    lines += ["", END_MARKER, ""]
    return "\n".join(lines)


def _update_doc(existing: str, section: str) -> str:
    if BEGIN_MARKER in existing and END_MARKER in existing:
        start = existing.index(BEGIN_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        # Preserve trailing newline behavior by replacing exact marker block.
        before = existing[:start].rstrip() + "\n\n"
        after = existing[end:].lstrip("\n")
        return before + section + after
    return existing.rstrip() + "\n\n" + section


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate schema docs snapshot from registry profiles.")
    ap.add_argument("--out", default="specs/schema/schema_v1.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    compiled, errs = compile_registry(repo_root)
    if compiled is None:
        for err in errs:
            print(err)
        return 1
    out = repo_root / str(ns.out)
    if not out.exists():
        print(f"{ns.out}: missing schema doc")
        return 1
    current = out.read_text(encoding="utf-8")
    updated = _update_doc(current, _generated_section(compiled))
    if ns.check:
        if current != updated:
            print(f"{ns.out}: generated registry snapshot is stale")
            return 1
        print("OK: schema docs snapshot is up to date")
        return 0
    out.write_text(updated, encoding="utf-8")
    print(f"wrote {ns.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
