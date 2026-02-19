from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any

import yaml

from spec_runner.ops_namespace import validate_registry_entry


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_tools_registry(root: Path, impl: str) -> list[dict[str, Any]]:
    path = root / "specs/tools" / impl / "tools_v1.yaml"
    if not path.exists():
        raise ValueError(f"missing tools registry for impl '{impl}': {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"tools registry must be a mapping: {path}")
    tools = payload.get("tools")
    if not isinstance(tools, list):
        raise TypeError(f"tools registry tools must be a list: {path}")
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(tools):
        if not isinstance(raw, dict):
            raise TypeError(f"tools[{i}] must be a mapping: {path}")
        diags = validate_registry_entry(raw, where=f"{path}:{i}")
        if diags:
            raise ValueError("; ".join(d.message for d in diags))
        out.append({str(k): v for k, v in raw.items()})
    return out


def resolve_tool(tools: list[dict[str, Any]], tool_id: str) -> dict[str, Any]:
    for tool in tools:
        if str(tool.get("tool_id", "")).strip() == tool_id:
            return tool
    raise ValueError(f"unknown orchestration tool_id: {tool_id}")


def run_tool_op(*, root: Path, impl: str, subcommand: str, args: list[str]) -> dict[str, Any]:
    adapter = root / "runners/public/runner_adapter.sh"
    started_at = _now_iso()
    cp = subprocess.run(
        [str(adapter), "--impl", impl, subcommand, *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    ended_at = _now_iso()
    return {
        "status": "pass" if cp.returncode == 0 else "fail",
        "started_at_utc": started_at,
        "ended_at_utc": ended_at,
        "duration_ms": 0,
        "data": {
            "exit_code": int(cp.returncode),
            "stdout": cp.stdout,
            "stderr": cp.stderr,
        },
        "diagnostics": [],
        "artifacts": [],
    }

