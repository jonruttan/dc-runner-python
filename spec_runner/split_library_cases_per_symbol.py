#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


_FENCE = re.compile(r"```yaml contract-spec\n(.*?)\n```", re.DOTALL)


def _iter_files(path: Path):
    if path.is_file():
        if path.suffix == ".md":
            yield path
        return
    if path.is_dir():
        for p in sorted(path.rglob("*.md")):
            if p.is_file():
                yield p


def _slug(symbol: str) -> str:
    out = re.sub(r"[^A-Za-z0-9]+", "-", symbol).strip("-").upper()
    return out or "SYMBOL"


def _dump_case(case: dict[str, Any]) -> str:
    return yaml.safe_dump(case, sort_keys=False, allow_unicode=False).rstrip("\n")


def _split_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    if str(case.get("type", "")).strip() != "spec_lang.export":
        return [case]
    defines = case.get("defines")
    if not isinstance(defines, dict):
        return [case]
    raw_public = defines.get("public")
    raw_private = defines.get("private")
    public_map = dict(raw_public) if isinstance(raw_public, dict) else {}
    private_map = dict(raw_private) if isinstance(raw_private, dict) else {}
    if len(public_map) == 1:
        return [case]
    out: list[dict[str, Any]] = []
    base_id = str(case.get("id", "LIB")).strip() or "LIB"
    base_title = str(case.get("title", "")).strip()
    if public_map:
        for idx, (name, expr) in enumerate(public_map.items(), start=1):
            item = dict(case)
            item["id"] = f"{base_id}-{idx:03d}-{_slug(name)}"
            if base_title:
                item["title"] = f"{base_title}: {name}"
            item["defines"] = {
                "public": {name: expr},
                "private": private_map if private_map else {},
            }
            out.append(item)
        return out
    # Hard-cut rule: if case had private-only symbols, promote each private symbol to public singleton case.
    if private_map:
        for idx, (name, expr) in enumerate(private_map.items(), start=1):
            item = dict(case)
            item["id"] = f"{base_id}-{idx:03d}-{_slug(name)}"
            if base_title:
                item["title"] = f"{base_title}: {name}"
            item["defines"] = {"public": {name: expr}}
            out.append(item)
    return out or [case]


def _rewrite(text: str) -> str:
    cursor = 0
    out: list[str] = []
    for m in _FENCE.finditer(text):
        out.append(text[cursor:m.start()])
        raw_block = m.group(1)
        try:
            case = yaml.safe_load(raw_block)
        except Exception:
            out.append(m.group(0))
            cursor = m.end()
            continue
        if not isinstance(case, dict):
            out.append(m.group(0))
            cursor = m.end()
            continue
        split = _split_case(case)
        if len(split) == 1 and split[0] is case:
            out.append(m.group(0))
            cursor = m.end()
            continue
        rendered = []
        for c in split:
            rendered.append("```yaml contract-spec\n" + _dump_case(c) + "\n```")
        out.append("\n\n".join(rendered))
        cursor = m.end()
    out.append(text[cursor:])
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Split spec_lang.export cases into one-public-symbol-per-case.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    ap.add_argument("paths", nargs="+", help="file or directory paths")
    ns = ap.parse_args(argv)

    changed: list[Path] = []
    for raw in ns.paths:
        p = Path(raw)
        for f in _iter_files(p):
            original = f.read_text(encoding="utf-8")
            updated = _rewrite(original)
            if updated != original:
                changed.append(f)
                if ns.write:
                    f.write_text(updated, encoding="utf-8")

    if ns.check:
        if changed:
            for f in changed:
                print(f"{f.as_posix()}: library case split drift")
            return 1
        print("OK: library cases are one-public-symbol per case")
        return 0

    print(f"OK: rewrote {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

