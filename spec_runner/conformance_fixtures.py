from __future__ import annotations

import json


def main(argv: list[str] | None = None) -> int:
    args = list(argv or [])
    if "--help" in args or "-h" in args:
        print("usage: conformance-fixture [--json]")
        return 0
    if "--json" in args:
        print(json.dumps({"ok": True, "source": "conformance-fixture"}))
        return 0
    print("conformance fixture ran")
    return 0
