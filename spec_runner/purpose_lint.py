from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

POLICY_REL_PATH = "specs/conformance/purpose_lint_v1.yaml"
_DEFAULT_MIN_WORDS = 8
_DEFAULT_PLACEHOLDERS = ("todo", "tbd", "fixme", "xxx")
_DEFAULT_SEVERITY_BY_CODE = {
    "PUR001": "warn",
    "PUR002": "warn",
    "PUR003": "warn",
    "PUR004": "error",
}
_VALID_SEVERITIES = {"info", "warn", "error"}


def default_purpose_lint_policy() -> dict[str, Any]:
    return {
        "version": 1,
        "default": {
            "min_words": _DEFAULT_MIN_WORDS,
            "placeholders": list(_DEFAULT_PLACEHOLDERS),
            "forbid_title_copy": True,
            "severity_by_code": dict(_DEFAULT_SEVERITY_BY_CODE),
        },
        "runtime": {},
    }


def _normalize_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _word_count(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", str(s)))


def _parse_profile(raw: Any, *, where: str, allow_enabled: bool, allow_runtime: bool) -> tuple[dict[str, Any], list[str]]:
    errs: list[str] = []
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return {}, [f"{where} must be a mapping"]
    allowed = {"min_words", "placeholders", "forbid_title_copy", "severity_by_code"}
    if allow_enabled:
        allowed.add("enabled")
    if allow_runtime:
        allowed.add("runtime")
    out: dict[str, Any] = {}
    for k in raw:
        if str(k) not in allowed:
            errs.append(f"{where} has unknown key: {k}")
    if "min_words" in raw:
        v = raw.get("min_words")
        if not isinstance(v, int) or v < 0:
            errs.append(f"{where}.min_words must be an integer >= 0")
        else:
            out["min_words"] = int(v)
    if "placeholders" in raw:
        v = raw.get("placeholders")
        if not isinstance(v, list):
            errs.append(f"{where}.placeholders must be a list")
        else:
            out["placeholders"] = [str(x).strip().lower() for x in v if str(x).strip()]
    if "forbid_title_copy" in raw:
        v = raw.get("forbid_title_copy")
        if not isinstance(v, bool):
            errs.append(f"{where}.forbid_title_copy must be a boolean")
        else:
            out["forbid_title_copy"] = bool(v)
    if "severity_by_code" in raw:
        v = raw.get("severity_by_code")
        if not isinstance(v, dict):
            errs.append(f"{where}.severity_by_code must be a mapping")
        else:
            sev_out: dict[str, str] = {}
            for k, val in v.items():
                code = str(k).strip().upper()
                sev = str(val).strip().lower()
                if not code:
                    errs.append(f"{where}.severity_by_code key must be non-empty")
                    continue
                if sev not in _VALID_SEVERITIES:
                    errs.append(
                        f"{where}.severity_by_code.{code} must be one of: info, warn, error"
                    )
                    continue
                sev_out[code] = sev
            out["severity_by_code"] = sev_out
    if allow_enabled and "enabled" in raw:
        v = raw.get("enabled")
        if not isinstance(v, bool):
            errs.append(f"{where}.enabled must be a boolean")
        else:
            out["enabled"] = bool(v)
    if allow_runtime and "runtime" in raw:
        v = str(raw.get("runtime", "")).strip()
        if not v:
            errs.append(f"{where}.runtime must be a non-empty string")
        else:
            out["runtime"] = v
    return out, errs


def load_purpose_lint_policy(repo_root: Path) -> tuple[dict[str, Any], list[str], Path]:
    base = default_purpose_lint_policy()
    policy_path = repo_root / POLICY_REL_PATH
    if not policy_path.exists():
        return base, [], policy_path

    errs: list[str] = []
    raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return base, [f"purpose lint policy must be a mapping: {policy_path}"], policy_path

    version = raw.get("version", 1)
    if version != 1:
        errs.append(f"purpose lint policy version must equal 1: {policy_path}")

    default_profile, profile_errs = _parse_profile(
        raw.get("default", {}),
        where=f"purpose lint policy default ({policy_path})",
        allow_enabled=False,
        allow_runtime=False,
    )
    errs.extend(profile_errs)

    runtime_raw = raw.get("runtime", {})
    runtime_out: dict[str, dict[str, Any]] = {}
    if not isinstance(runtime_raw, dict):
        errs.append(f"purpose lint policy runtime must be a mapping: {policy_path}")
        runtime_raw = {}
    for runtime, cfg in runtime_raw.items():
        name = str(runtime).strip()
        if not name:
            errs.append(f"purpose lint policy runtime key must be non-empty: {policy_path}")
            continue
        parsed, per_errs = _parse_profile(
            cfg,
            where=f"purpose lint policy runtime.{name} ({policy_path})",
            allow_enabled=False,
            allow_runtime=False,
        )
        errs.extend(per_errs)
        runtime_out[name] = parsed

    merged = default_purpose_lint_policy()
    merged["default"].update(default_profile)
    merged["runtime"] = runtime_out
    return merged, errs, policy_path


def resolve_purpose_lint_config(case: dict[str, Any], policy: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errs: list[str] = []
    cfg = dict(policy.get("default") or {})
    raw_runtime = policy.get("runtime")
    runtime_map: dict[str, Any] = raw_runtime if isinstance(raw_runtime, dict) else {}
    override_raw = case.get("purpose_lint")
    override: dict[str, Any] = {}
    if override_raw is not None:
        parsed, per_errs = _parse_profile(
            override_raw,
            where="purpose_lint",
            allow_enabled=True,
            allow_runtime=True,
        )
        errs.extend(per_errs)
        override = parsed

    runtime_name = str(override.get("runtime", "")).strip()
    if runtime_name:
        profile = runtime_map.get(runtime_name)
        if not isinstance(profile, dict):
            errs.append(f"purpose_lint.runtime references unknown runtime profile: {runtime_name}")
        else:
            cfg.update(profile)

    cfg.update({k: v for k, v in override.items() if k in {"min_words", "placeholders", "forbid_title_copy", "enabled"}})
    if "severity_by_code" in override:
        merged_sev = dict(cfg.get("severity_by_code") or {})
        merged_sev.update(override.get("severity_by_code") or {})
        cfg["severity_by_code"] = merged_sev
    cfg.setdefault("enabled", True)
    cfg["min_words"] = int(cfg.get("min_words", _DEFAULT_MIN_WORDS))
    cfg["forbid_title_copy"] = bool(cfg.get("forbid_title_copy", True))
    cfg["placeholders"] = [str(x).strip().lower() for x in cfg.get("placeholders", list(_DEFAULT_PLACEHOLDERS))]
    sev = cfg.get("severity_by_code")
    if not isinstance(sev, dict):
        sev = {}
    merged_sev = dict(_DEFAULT_SEVERITY_BY_CODE)
    for k, v in sev.items():
        code = str(k).strip().upper()
        level = str(v).strip().lower()
        if code and level in _VALID_SEVERITIES:
            merged_sev[code] = level
    cfg["severity_by_code"] = merged_sev
    cfg["runtime"] = runtime_name or None
    return cfg, errs


def purpose_quality_warnings(title: str, purpose: str, cfg: dict[str, Any], *, honor_enabled: bool = True) -> list[str]:
    if honor_enabled and not bool(cfg.get("enabled", True)):
        return []
    warns: list[str] = []
    stitle = str(title).strip()
    spurpose = str(purpose).strip()
    if bool(cfg.get("forbid_title_copy", True)) and stitle and _normalize_sentence(stitle) == _normalize_sentence(spurpose):
        warns.append("purpose duplicates title")
    min_words = int(cfg.get("min_words", _DEFAULT_MIN_WORDS))
    wc = _word_count(spurpose)
    if wc and wc < min_words:
        warns.append(f"purpose word count {wc} below minimum {min_words}")
    placeholder_set = {str(x).lower() for x in cfg.get("placeholders", [])}
    purpose_tokens = {tok.lower() for tok in re.findall(r"[A-Za-z0-9_]+", spurpose)}
    bad_tokens = sorted(tok for tok in purpose_tokens if tok in placeholder_set)
    if bad_tokens:
        warns.append(f"purpose contains placeholder token(s): {', '.join(bad_tokens)}")
    return warns


def warning_severity_for_code(code: str, cfg: dict[str, Any]) -> str:
    sev = cfg.get("severity_by_code")
    if isinstance(sev, dict):
        level = str(sev.get(str(code).upper(), "")).strip().lower()
        if level in _VALID_SEVERITIES:
            return level
    return _DEFAULT_SEVERITY_BY_CODE.get(str(code).upper(), "warn")
