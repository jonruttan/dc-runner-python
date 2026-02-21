from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _repo_commit_sha(root: Path) -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=False, capture_output=True, text=True)
    if proc.returncode == 0:
        out = (proc.stdout or "").strip()
        if out:
            return out
    return "unknown"


def _load_registry(root: Path) -> tuple[Path, dict[str, Any]]:
    candidates = [
        root / "specs/schema/runner_certification_registry_v2.yaml",
        root / "specs/upstream/data-contracts/specs/schema/runner_certification_registry_v2.yaml",
    ]
    for path in candidates:
        if path.exists():
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return path, payload
            raise SystemExit(f"ERROR: invalid registry root in {path}")
    raise SystemExit("ERROR: runner certification registry v2 not found")


def _normalize_intent(entry: dict[str, Any]) -> dict[str, Any]:
    checks = sorted({str(x).strip() for x in (entry.get("required_core_checks") or []) if str(x).strip()})
    cases = sorted({str(x).strip() for x in (entry.get("required_core_cases") or []) if str(x).strip()})
    subset_rows = []
    for item in (entry.get("command_contract_subset") or []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        args = [str(x) for x in (item.get("args") or [])]
        expect_exit = sorted({int(x) for x in (item.get("expect_exit") or [0])})
        subset_rows.append({"name": name, "args": args, "expect_exit": expect_exit})
    subset_rows.sort(key=lambda row: (row["name"], "\x1f".join(row["args"]), ",".join(map(str, row["expect_exit"]))))
    return {
        "required_core_checks": checks,
        "required_core_cases": cases,
        "command_contract_subset": subset_rows,
        "registry_ref": {
            "path": "/specs/schema/runner_certification_registry_v2.yaml",
            "version": 2,
        },
    }


def _run_command(root: Path, name: str, args: list[str]) -> int:
    command_map = {
        "governance": ["./runner_adapter.sh", "governance", *args],
        "style-check": ["./runner_adapter.sh", "style-check", *args],
        "docs-generate-check": ["./runner_adapter.sh", "spec-runner", "docs-generate-check", *args],
    }
    cmd = command_map.get(name)
    if cmd is None:
        return 2
    proc = subprocess.run(cmd, cwd=root, check=False)
    return int(proc.returncode)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Emit runner execution certificate v2 artifacts")
    ap.add_argument("--runner", required=True)
    ap.add_argument("--root", default=".")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv)
    runner_id = str(ns.runner).strip()
    if not runner_id:
        raise SystemExit("ERROR: --runner must be non-empty")
    root = Path(ns.root).resolve()
    reg_path, registry = _load_registry(root)
    if int(registry.get("version", 0)) != 2:
        raise SystemExit(f"ERROR: unsupported registry version in {reg_path}: {registry.get('version')}")

    entry: dict[str, Any] | None = None
    for row in registry.get("runners") or []:
        if isinstance(row, dict) and str(row.get("runner_id", "")).strip() == runner_id:
            entry = row
            break
    if entry is None:
        raise SystemExit(f"ERROR: unknown runner id for certification: {runner_id}")

    runner_class = str(entry.get("class", "")).strip()
    runner_status = str(entry.get("status", "")).strip()
    if runner_class not in {"required", "compatibility_non_blocking"}:
        raise SystemExit(f"ERROR: invalid class for {runner_id}: {runner_class}")

    checks: list[dict[str, Any]] = []

    def add_check(group: str, cid: str, status: str, exit_code: int, detail: str) -> None:
        checks.append(
            {
                "group": group,
                "id": cid,
                "status": status,
                "exit_code": int(exit_code),
                "detail": detail,
            }
        )

    add_check("contract", "registry.entry.shape", "pass", 0, "runner certification registry entry parsed and validated")

    blocking = runner_class == "required" and runner_status == "active"

    command_specs: list[dict[str, Any]] = []
    for row in entry.get("command_contract_subset") or []:
        if isinstance(row, dict):
            command_specs.append(row)

    if runner_status != "active":
        add_check("command", "command.subset", "skip", 0, "runner status is not active; command subset execution skipped")
    else:
        for spec in command_specs:
            name = str(spec.get("name", "")).strip()
            if not name:
                continue
            args = [str(x) for x in (spec.get("args") or [])]
            expected = sorted({int(x) for x in (spec.get("expect_exit") or [0])})
            code = _run_command(root, name, args)
            if code in expected:
                add_check("command", f"command.{name}", "pass", code, "command contract subset matched expected exit semantics")
            else:
                add_check("command", f"command.{name}", "fail", code, f"unexpected exit code; expected one of {expected}")

    if runner_status != "active":
        add_check("governance-sync", "governance.required_core_checks", "skip", 0, "runner status is not active; governance sync checks skipped")
        add_check("conformance", "conformance.required_core_cases", "skip", 0, "runner status is not active; conformance subset skipped")
    else:
        add_check("governance-sync", "governance.required_core_checks", "skip", 0, "runner-specific governance checks are not executed in certification shim")
        add_check("conformance", "conformance.required_core_cases", "skip", 0, "runner-specific conformance checks are not executed in certification shim")

    passed = sum(1 for row in checks if row["status"] == "pass")
    failed = sum(1 for row in checks if row["status"] == "fail")
    skipped = sum(1 for row in checks if row["status"] == "skip")
    summary_status = "pass" if failed == 0 else "fail"

    entrypoints = entry.get("entrypoints") if isinstance(entry.get("entrypoints"), dict) else {}
    implementation_repo = str((entrypoints or {}).get("implementation_repo", "unknown"))

    execution_intent = _normalize_intent(entry)
    intent_hash = _sha256_hex(_canonical_json(execution_intent))

    payload: dict[str, Any] = {
        "version": 2,
        "runner": {
            "runner_id": runner_id,
            "class": runner_class,
            "status": runner_status,
            "blocking": blocking,
            "implementation_repo": implementation_repo,
            "commit_sha": _repo_commit_sha(root),
            "certified_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        "execution_intent": execution_intent,
        "equivalence": {
            "normalization_version": "intent-v1",
            "hash_algorithm": "sha256",
            "intent_hash": intent_hash,
        },
        "summary": {
            "status": summary_status,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "blocking": blocking,
        },
        "checks": checks,
        "proof": {
            "canonicalization": "json-c14n-v1",
            "payload_sha256": "",
        },
    }
    payload_hash = _sha256_hex(_canonical_json(payload))
    payload["proof"]["payload_sha256"] = payload_hash

    artifacts = entry.get("artifact_contract") if isinstance(entry.get("artifact_contract"), dict) else {}
    json_out = str(artifacts.get("json_out", "/.artifacts/runner-certification-{runner}.json")).replace("{runner}", runner_id)
    md_out = str(artifacts.get("md_out", "/.artifacts/runner-certification-{runner}.md")).replace("{runner}", runner_id)
    json_path = root / json_out.lstrip("/")
    md_path = root / md_out.lstrip("/")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Runner Certification Report",
        "",
        f"- version: `{payload['version']}`",
        f"- runner_id: `{payload['runner']['runner_id']}`",
        f"- class: `{payload['runner']['class']}`",
        f"- status: `{payload['runner']['status']}`",
        f"- blocking: `{payload['runner']['blocking']}`",
        f"- implementation_repo: `{payload['runner']['implementation_repo']}`",
        f"- commit_sha: `{payload['runner']['commit_sha']}`",
        f"- certified_at: `{payload['runner']['certified_at']}`",
        f"- equivalence.intent_hash: `{payload['equivalence']['intent_hash']}`",
        f"- proof.payload_sha256: `{payload['proof']['payload_sha256']}`",
        f"- summary.status: `{payload['summary']['status']}`",
        f"- summary.passed: `{payload['summary']['passed']}`",
        f"- summary.failed: `{payload['summary']['failed']}`",
        f"- summary.skipped: `{payload['summary']['skipped']}`",
        "",
        "## Checks",
        "",
        "| group | id | status | exit_code | detail |",
        "|---|---|---:|---:|---|",
    ]
    for row in checks:
        lines.append(
            f"| `{row['group']}` | `{row['id']}` | `{row['status']}` | `{row['exit_code']}` | {row['detail']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"OK: runner certification report written: {json_path}")
    print(f"OK: runner certification report written: {md_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
