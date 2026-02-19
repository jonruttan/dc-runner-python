from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

from spec_runner.compiler import compile_external_case
from spec_runner.components.assertion_engine import run_assertions_with_context
from spec_runner.components.effects.http_ops import run_http_op
from spec_runner.components.execution_context import build_execution_context
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.components.subject_router import resolve_subject_for_target
from spec_runner.virtual_paths import contract_root_for, resolve_contract_path

_OAUTH_TOKEN_CACHE: dict[tuple[str, str, str, str], tuple[str, float]] = {}
_SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
_TEMPLATE_STEP_PATTERN = re.compile(r"\{\{\s*steps\.([A-Za-z0-9_.-]+)\s*\}\}")
_TEMPLATE_CHAIN_PATTERN = re.compile(r"\{\{\s*chain\.([A-Za-z0-9_.-]+)\s*\}\}")


def _resolve_relative_subject_path(doc_path: Path, rel: str) -> Path:
    try:
        return resolve_contract_path(
            contract_root_for(doc_path), str(rel), field="api.http request.url path"
        )
    except ValueError as e:
        raise ValueError(str(e)) from e


def _is_live_network_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme.lower() in {"http", "https"}


def _has_header(headers: dict[str, str], key: str) -> bool:
    want = key.strip().lower()
    return any(str(k).strip().lower() == want for k in headers)


def _get_header(headers: dict[str, str], key: str) -> str | None:
    want = key.strip().lower()
    for k, v in headers.items():
        if str(k).strip().lower() == want:
            return str(v)
    return None


def _set_header(headers: dict[str, str], key: str, value: str) -> None:
    want = key.strip().lower()
    for existing in list(headers.keys()):
        if str(existing).strip().lower() == want:
            headers[existing] = value
            return
    headers[key] = value


def _csv_header_values(raw: str | None) -> list[str]:
    if raw is None:
        return []
    out: list[str] = []
    for part in str(raw).split(","):
        token = part.strip()
        if token:
            out.append(token)
    return out


def _parse_bool_header(raw: str | None) -> bool | None:
    if raw is None:
        return None
    val = str(raw).strip().lower()
    if val == "true":
        return True
    if val == "false":
        return False
    return None


def _parse_int_header(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except Exception:
        return None


def _normalize_cors(headers: dict[str, str]) -> dict[str, Any]:
    vary_values = [x.lower() for x in _csv_header_values(_get_header(headers, "Vary"))]
    return {
        "allow_origin": _get_header(headers, "Access-Control-Allow-Origin"),
        "allow_methods": _csv_header_values(_get_header(headers, "Access-Control-Allow-Methods")),
        "allow_headers": _csv_header_values(_get_header(headers, "Access-Control-Allow-Headers")),
        "expose_headers": _csv_header_values(_get_header(headers, "Access-Control-Expose-Headers")),
        "allow_credentials": _parse_bool_header(_get_header(headers, "Access-Control-Allow-Credentials")),
        "max_age": _parse_int_header(_get_header(headers, "Access-Control-Max-Age")),
        "vary_origin": "origin" in vary_values,
    }


def _env_required(ctx, name: str) -> str:
    env_name = str(name).strip()
    if not env_name:
        raise ValueError("api.http oauth env var name must be a non-empty string")
    raw = None
    if getattr(ctx, "env", None) is not None:
        raw = ctx.env.get(env_name)
    if raw is None:
        raw = os.environ.get(env_name)
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"api.http oauth env var is required: {env_name}")
    return str(raw)


def _parse_api_http_harness(case_harness: dict[str, Any]) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    api_http = case_harness.get("api_http") if isinstance(case_harness, dict) else None
    if api_http is None:
        return "deterministic", None, None
    if not isinstance(api_http, dict):
        raise TypeError("harness.api_http must be a mapping")
    mode = str(api_http.get("mode", "deterministic")).strip().lower() or "deterministic"
    if mode not in {"deterministic", "live"}:
        raise ValueError("harness.api_http.mode must be one of: deterministic, live")

    scenario = api_http.get("scenario")
    if scenario is not None and not isinstance(scenario, dict):
        raise TypeError("harness.api_http.scenario must be a mapping")

    auth = api_http.get("auth")
    if auth is None:
        return mode, None, scenario
    if not isinstance(auth, dict):
        raise TypeError("harness.api_http.auth must be a mapping")
    oauth = auth.get("oauth")
    if oauth is None:
        return mode, None, scenario
    if not isinstance(oauth, dict):
        raise TypeError("harness.api_http.auth.oauth must be a mapping")

    grant_type = str(oauth.get("grant_type", "client_credentials")).strip().lower() or "client_credentials"
    if grant_type != "client_credentials":
        raise ValueError("api.http oauth grant_type must be client_credentials")

    token_url = str(oauth.get("token_url", "")).strip()
    if not token_url:
        raise ValueError("api.http oauth token_url is required")

    client_id_env = str(oauth.get("client_id_env", "")).strip()
    if not client_id_env:
        raise ValueError("api.http oauth client_id_env is required")
    client_secret_env = str(oauth.get("client_secret_env", "")).strip()
    if not client_secret_env:
        raise ValueError("api.http oauth client_secret_env is required")

    auth_style = str(oauth.get("auth_style", "basic")).strip().lower() or "basic"
    if auth_style not in {"basic", "body"}:
        raise ValueError("api.http oauth auth_style must be one of: basic, body")

    token_field = str(oauth.get("token_field", "access_token")).strip() or "access_token"
    expires_field = str(oauth.get("expires_field", "expires_in")).strip() or "expires_in"

    skew_raw = oauth.get("refresh_skew_seconds", 30)
    try:
        refresh_skew_seconds = int(skew_raw)
    except Exception as e:  # noqa: BLE001
        raise TypeError("api.http oauth refresh_skew_seconds must be an integer") from e
    if refresh_skew_seconds < 0:
        raise ValueError("api.http oauth refresh_skew_seconds must be >= 0")

    scope = oauth.get("scope")
    audience = oauth.get("audience")

    return mode, {
        "grant_type": grant_type,
        "token_url": token_url,
        "client_id_env": client_id_env,
        "client_secret_env": client_secret_env,
        "scope": None if scope is None else str(scope),
        "audience": None if audience is None else str(audience),
        "auth_style": auth_style,
        "token_field": token_field,
        "expires_field": expires_field,
        "refresh_skew_seconds": refresh_skew_seconds,
    }, scenario


def _load_token_payload_from_url(
    case,
    *,
    token_url: str,
    timeout_seconds: float,
    mode: str,
    client_id: str,
    client_secret: str,
    grant_type: str,
    scope: str | None,
    audience: str | None,
    auth_style: str,
) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(token_url)
    if not parsed.scheme:
        path = _resolve_relative_subject_path(case.doc_path, token_url)
        return json.loads(path.read_text(encoding="utf-8"))
    if parsed.scheme == "file":
        path = Path(urllib.parse.unquote(parsed.path))
        return json.loads(path.read_text(encoding="utf-8"))
    if _is_live_network_url(token_url):
        if mode != "live":
            raise ValueError("api.http oauth token_url network fetch requires harness.api_http.mode=live")
        form: dict[str, str] = {"grant_type": grant_type}
        if scope:
            form["scope"] = str(scope)
        if audience:
            form["audience"] = str(audience)
        headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        if auth_style == "basic":
            pair = f"{client_id}:{client_secret}".encode("utf-8")
            headers["Authorization"] = "Basic " + base64.b64encode(pair).decode("ascii")
        else:
            form["client_id"] = client_id
            form["client_secret"] = client_secret
        data = urllib.parse.urlencode(form).encode("utf-8")
        req = urllib.request.Request(url=token_url, method="POST", headers=headers, data=data)
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:  # nosec B310
                body = resp.read().decode("utf-8")
        except HTTPError as e:
            raise RuntimeError(f"api.http oauth token request failed with HTTP {int(e.code)}") from e
        except URLError as e:
            raise RuntimeError("api.http oauth token request failed") from e
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError as e:
            raise RuntimeError("api.http oauth token response is not valid JSON") from e
        if not isinstance(parsed_body, dict):
            raise RuntimeError("api.http oauth token response must be a JSON object")
        return parsed_body
    raise ValueError(f"api.http oauth token_url scheme is not supported: {parsed.scheme}")


def _oauth_access_token(case, *, ctx, oauth: dict[str, Any], timeout_seconds: float, mode: str) -> tuple[str, bool, float]:
    token_url = str(oauth["token_url"])
    scope = oauth.get("scope")
    audience = oauth.get("audience")
    cache_key = (
        token_url,
        str(oauth["client_id_env"]),
        "" if scope is None else str(scope),
        "" if audience is None else str(audience),
    )
    now = time.time()
    cached = _OAUTH_TOKEN_CACHE.get(cache_key)
    if cached is not None:
        token, expires_at = cached
        if now < expires_at - int(oauth["refresh_skew_seconds"]):
            return token, True, 0.0

    client_id = _env_required(ctx, str(oauth["client_id_env"]))
    client_secret = _env_required(ctx, str(oauth["client_secret_env"]))
    started = time.perf_counter()
    payload = _load_token_payload_from_url(
        case,
        token_url=token_url,
        timeout_seconds=timeout_seconds,
        mode=mode,
        client_id=client_id,
        client_secret=client_secret,
        grant_type=str(oauth["grant_type"]),
        scope=None if scope is None else str(scope),
        audience=None if audience is None else str(audience),
        auth_style=str(oauth["auth_style"]),
    )
    fetch_ms = (time.perf_counter() - started) * 1000.0
    token_field = str(oauth["token_field"])
    raw_token = payload.get(token_field)
    if raw_token is None or str(raw_token).strip() == "":
        raise RuntimeError(f"api.http oauth token response missing field: {token_field}")
    access_token = str(raw_token)

    expires_in = payload.get(str(oauth["expires_field"]), 3600)
    try:
        expires_seconds = float(expires_in)
    except Exception:
        expires_seconds = 3600.0
    _OAUTH_TOKEN_CACHE[cache_key] = (access_token, now + max(expires_seconds, 0.0))
    return access_token, False, fetch_ms


def _fetch_response(
    case,
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    body_bytes: bytes | None,
    timeout_seconds: float,
    mode: str,
) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        subject = _resolve_relative_subject_path(case.doc_path, url)
        text = subject.read_text(encoding="utf-8")
        return {"status": 200, "headers": {}, "body_text": text}

    if parsed.scheme == "file":
        subject = Path(urllib.parse.unquote(parsed.path))
        text = subject.read_text(encoding="utf-8")
        return {"status": 200, "headers": {}, "body_text": text}

    if _is_live_network_url(url) and mode != "live":
        raise ValueError("api.http request.url network fetch requires harness.api_http.mode=live")

    req = urllib.request.Request(url=url, method=method, headers=headers, data=body_bytes)
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:  # nosec B310 (explicit runtime behavior)
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            hdrs = {str(k).strip(): str(v).strip() for k, v in resp.headers.items()}
            status = int(getattr(resp, "status", None) or resp.getcode() or 0)
            return {"status": status, "headers": hdrs, "body_text": text}
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        hdrs = {str(k).strip(): str(v).strip() for k, v in dict(e.headers).items()} if e.headers else {}
        return {"status": int(e.code), "headers": hdrs, "body_text": body}
    except URLError as e:
        raise RuntimeError("api.http request failed") from e


def _json_or_none(body_text: str) -> Any:
    raw = str(body_text)
    if raw.strip() == "":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _merge_query(url: str, query: dict[str, Any] | None) -> str:
    if not query:
        return url
    parts = urllib.parse.urlsplit(url)
    existing = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    append: list[tuple[str, str]] = []
    for key in sorted(query.keys(), key=lambda x: str(x)):
        val = query[key]
        if isinstance(val, list):
            for item in val:
                append.append((str(key), "" if item is None else str(item)))
        else:
            append.append((str(key), "" if val is None else str(val)))
    merged = urllib.parse.urlencode(existing + append, doseq=True)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, merged, parts.fragment))


def _render_step_template(raw: str, *, steps: dict[str, dict[str, Any]]) -> str:
    text = str(raw)

    def _replace(match: re.Match[str]) -> str:
        dotted = match.group(1)
        parts = [p for p in dotted.split(".") if p]
        if len(parts) < 2:
            raise ValueError(f"api.http scenario template must reference a step field: {dotted}")
        step_id = parts[0]
        current: Any = steps.get(step_id)
        if current is None:
            raise ValueError(f"api.http scenario template references unknown step: {step_id}")
        for key in parts[1:]:
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"api.http scenario template path not found: steps.{dotted}")
            current = current[key]
        if isinstance(current, (dict, list)):
            return json.dumps(current, ensure_ascii=False, separators=(",", ":"))
        if current is None:
            return ""
        return str(current)

    return _TEMPLATE_STEP_PATTERN.sub(_replace, text)


def _render_request_template(step: dict[str, Any], *, steps: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rendered = dict(step)
    if "url" in rendered:
        rendered["url"] = _render_step_template(str(rendered["url"]), steps=steps)
    raw_headers = rendered.get("headers")
    if isinstance(raw_headers, dict):
        headers: dict[str, str] = {}
        for k, v in raw_headers.items():
            headers[str(k)] = _render_step_template(str(v), steps=steps)
        rendered["headers"] = headers
    if "body_text" in rendered and rendered.get("body_text") is not None:
        rendered["body_text"] = _render_step_template(str(rendered["body_text"]), steps=steps)
    return rendered


def _render_chain_template(raw: str, *, chain_state: dict[str, Any]) -> str:
    text = str(raw)

    def _replace(match: re.Match[str]) -> str:
        dotted = match.group(1)
        parts = [p for p in dotted.split(".") if p]
        if len(parts) < 2:
            raise ValueError(f"api.http chain template must reference step and export: {dotted}")
        step_id = parts[0]
        current: Any = chain_state.get(step_id)
        if current is None:
            raise ValueError(f"api.http chain template references unknown step: {step_id}")
        for key in parts[1:]:
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"api.http chain template path not found: chain.{dotted}")
            current = current[key]
        if isinstance(current, (dict, list)):
            return json.dumps(current, ensure_ascii=False, separators=(",", ":"))
        if current is None:
            return ""
        return str(current)

    return _TEMPLATE_CHAIN_PATTERN.sub(_replace, text)


def _render_request_chain(step: dict[str, Any], *, chain_state: dict[str, Any]) -> dict[str, Any]:
    rendered = dict(step)
    if "url" in rendered:
        rendered["url"] = _render_chain_template(str(rendered["url"]), chain_state=chain_state)
    raw_headers = rendered.get("headers")
    if isinstance(raw_headers, dict):
        headers: dict[str, str] = {}
        for k, v in raw_headers.items():
            headers[str(k)] = _render_chain_template(str(v), chain_state=chain_state)
        rendered["headers"] = headers
    if "body_text" in rendered and rendered.get("body_text") is not None:
        rendered["body_text"] = _render_chain_template(str(rendered["body_text"]), chain_state=chain_state)
    return rendered


def _prepare_request(*, request: dict[str, Any]) -> tuple[str, str, dict[str, str], bytes | None, dict[str, Any] | None]:
    method = str(request.get("method", "")).strip().upper()
    if not method:
        raise ValueError("api.http request.method is required")
    if method not in _SUPPORTED_METHODS:
        allowed = ", ".join(sorted(_SUPPORTED_METHODS))
        raise ValueError(f"api.http request.method must be one of: {allowed}")

    url = str(request.get("url", "")).strip()
    if not url:
        raise ValueError("api.http request.url is required")

    raw_headers = request.get("headers") or {}
    if not isinstance(raw_headers, dict):
        raise TypeError("api.http request.headers must be a mapping")
    headers = {str(k).strip(): str(v).strip() for k, v in raw_headers.items()}

    query = request.get("query")
    if query is not None and not isinstance(query, dict):
        raise TypeError("api.http request.query must be a mapping")
    merged_url = _merge_query(url, query)

    body_text = request.get("body_text")
    body_json = request.get("body_json")
    if body_text is not None and body_json is not None:
        raise ValueError("api.http request.body_text and request.body_json are mutually exclusive")
    body_bytes: bytes | None = None
    if body_text is not None:
        body_bytes = str(body_text).encode("utf-8")
    elif body_json is not None:
        body_bytes = json.dumps(body_json, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if not _has_header(headers, "Content-Type"):
            headers["Content-Type"] = "application/json"

    cors = request.get("cors")
    if cors is not None:
        if not isinstance(cors, dict):
            raise TypeError("api.http request.cors must be a mapping")
        origin = cors.get("origin")
        if origin is not None and str(origin).strip() != "" and not _has_header(headers, "Origin"):
            _set_header(headers, "Origin", str(origin).strip())
        preflight = bool(cors.get("preflight", False))
        if preflight:
            if method != "OPTIONS":
                raise ValueError("api.http request.cors.preflight requires request.method OPTIONS")
            request_method = str(cors.get("request_method", "")).strip().upper()
            if not request_method:
                raise ValueError("api.http request.cors.request_method is required for preflight")
            _set_header(headers, "Access-Control-Request-Method", request_method)
            request_headers = cors.get("request_headers")
            if request_headers is not None:
                if not isinstance(request_headers, list):
                    raise TypeError("api.http request.cors.request_headers must be a list")
                _set_header(
                    headers,
                    "Access-Control-Request-Headers",
                    ", ".join(str(x).strip() for x in request_headers if str(x).strip()),
                )

    return method, merged_url, headers, body_bytes, cors if isinstance(cors, dict) else None


def _scenario_command(cmd_obj: Any, *, field: str) -> list[str]:
    if not isinstance(cmd_obj, list) or not cmd_obj:
        raise TypeError(f"{field} must be a non-empty list of strings")
    out: list[str] = []
    for item in cmd_obj:
        token = str(item).strip()
        if not token:
            raise ValueError(f"{field} entries must be non-empty strings")
        out.append(token)
    return out


def _scenario_cwd(case, raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    path = resolve_contract_path(contract_root_for(case.doc_path), str(raw), field=field)
    return str(path)


def _scenario_env(raw: Any, *, field: str) -> dict[str, str] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise TypeError(f"{field} must be a mapping")
    return {str(k): str(v) for k, v in raw.items()}


def _run_scenario(
    case,
    *,
    ctx,
    scenario: dict[str, Any],
    requests: list[dict[str, Any]],
    timeout_seconds: float,
    mode: str,
    oauth: dict[str, Any] | None,
    initial_oauth_context: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    fail_fast = bool(scenario.get("fail_fast", True))
    setup = scenario.get("setup")
    teardown = scenario.get("teardown")
    if setup is not None and not isinstance(setup, dict):
        raise TypeError("harness.api_http.scenario.setup must be a mapping")
    if teardown is not None and not isinstance(teardown, dict):
        raise TypeError("harness.api_http.scenario.teardown must be a mapping")

    scenario_meta = {
        "setup_started": False,
        "setup_ready": False,
        "teardown_ran": False,
        "step_count": len(requests),
        "step_ids": [str(step.get("id", "")).strip() for step in requests],
    }

    bg_process: subprocess.Popen[str] | None = None
    step_results: list[dict[str, Any]] = []
    step_index: dict[str, dict[str, Any]] = {}

    def _execute_one(step_request: dict[str, Any]) -> dict[str, Any]:
        rendered = _render_request_template(step_request, steps=step_index)
        method, url, headers, body_bytes, _cors_req = _prepare_request(request=rendered)
        oauth_context = dict(initial_oauth_context)
        if oauth is not None:
            token, used_cached_token, token_fetch_ms = _oauth_access_token(
                case,
                ctx=ctx,
                oauth=oauth,
                timeout_seconds=timeout_seconds,
                mode=mode,
            )
            if not _has_header(headers, "Authorization"):
                headers["Authorization"] = f"Bearer {token}"
            oauth_context.update(
                {
                    "token_fetch_ms": token_fetch_ms,
                    "used_cached_token": used_cached_token,
                }
            )
        response = _fetch_response(
            case,
            method=method,
            url=url,
            headers=headers,
            body_bytes=body_bytes,
            timeout_seconds=timeout_seconds,
            mode=mode,
        )
        body_text = str(response["body_text"])
        body_json = _json_or_none(body_text)
        cors_json = _normalize_cors(response["headers"])
        return {
            "id": str(step_request.get("id", "")).strip(),
            "method": method,
            "url": url,
            "status": int(response["status"]),
            "headers": response["headers"],
            "body_text": body_text,
            "body_json": body_json,
            "cors_json": cors_json,
            "oauth_context": oauth_context,
        }

    try:
        if setup is not None:
            setup_cmd = _scenario_command(setup.get("command"), field="harness.api_http.scenario.setup.command")
            setup_cwd = _scenario_cwd(case, setup.get("cwd"), field="harness.api_http.scenario.setup.cwd")
            setup_env = _scenario_env(setup.get("env"), field="harness.api_http.scenario.setup.env")
            setup_ready_probe = setup.get("ready_probe")
            scenario_meta["setup_started"] = True
            if setup_ready_probe is not None:
                if not isinstance(setup_ready_probe, dict):
                    raise TypeError("harness.api_http.scenario.setup.ready_probe must be a mapping")
                merged_env = os.environ.copy()
                if setup_env:
                    merged_env.update(setup_env)
                bg_process = subprocess.Popen(
                    setup_cmd,
                    cwd=setup_cwd,
                    env=merged_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                probe_url = str(setup_ready_probe.get("url", "")).strip()
                if not probe_url:
                    raise ValueError("harness.api_http.scenario.setup.ready_probe.url is required")
                probe_method = str(setup_ready_probe.get("method", "GET")).strip().upper() or "GET"
                expect_status_in_raw = setup_ready_probe.get("expect_status_in", [200, 204])
                if not isinstance(expect_status_in_raw, list) or not expect_status_in_raw:
                    raise TypeError("harness.api_http.scenario.setup.ready_probe.expect_status_in must be a non-empty list")
                expect_status_in = {int(x) for x in expect_status_in_raw}
                timeout_ms = int(setup_ready_probe.get("timeout_ms", 10000))
                interval_ms = int(setup_ready_probe.get("interval_ms", 200))
                deadline = time.time() + max(timeout_ms, 1) / 1000.0
                while time.time() < deadline:
                    if bg_process.poll() is not None:
                        raise RuntimeError("api.http scenario setup process exited before ready_probe succeeded")
                    try:
                        probe_resp = _fetch_response(
                            case,
                            method=probe_method,
                            url=probe_url,
                            headers={},
                            body_bytes=None,
                            timeout_seconds=timeout_seconds,
                            mode=mode,
                        )
                        if int(probe_resp["status"]) in expect_status_in:
                            scenario_meta["setup_ready"] = True
                            break
                    except Exception:
                        pass
                    time.sleep(max(interval_ms, 1) / 1000.0)
                if not scenario_meta["setup_ready"]:
                    raise RuntimeError("api.http scenario setup ready_probe timed out")
            else:
                subprocess.run(
                    setup_cmd,
                    cwd=setup_cwd,
                    env=None if setup_env is None else {**os.environ, **setup_env},
                    check=True,
                    capture_output=True,
                    text=True,
                )
                scenario_meta["setup_ready"] = True

        for step in requests:
            step_result = _execute_one(step)
            step_id = str(step_result["id"])
            if not step_id:
                raise ValueError("api.http scenario step id is required")
            step_results.append(step_result)
            step_index[step_id] = step_result
    except Exception:
        if fail_fast:
            raise
    finally:
        if teardown is not None:
            teardown_cmd = _scenario_command(teardown.get("command"), field="harness.api_http.scenario.teardown.command")
            teardown_cwd = _scenario_cwd(case, teardown.get("cwd"), field="harness.api_http.scenario.teardown.cwd")
            teardown_env = _scenario_env(teardown.get("env"), field="harness.api_http.scenario.teardown.env")
            try:
                subprocess.run(
                    teardown_cmd,
                    cwd=teardown_cwd,
                    env=None if teardown_env is None else {**os.environ, **teardown_env},
                    check=False,
                    capture_output=True,
                    text=True,
                )
            finally:
                scenario_meta["teardown_ran"] = True
        if bg_process is not None and bg_process.poll() is None:
            bg_process.terminate()
            try:
                bg_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                bg_process.kill()

    if not step_results:
        raise RuntimeError("api.http scenario did not execute any request steps")

    last = step_results[-1]
    return (
        {
            "status": last["status"],
            "headers": last["headers"],
            "body_text": last["body_text"],
            "body_json": last["body_json"],
            "cors_json": last["cors_json"],
            "method": last["method"],
            "url": last["url"],
            "oauth_context": last["oauth_context"],
        },
        step_results,
        scenario_meta,
        step_index,
    )


def run(case, *, ctx) -> None:
    if hasattr(case, "test") and hasattr(case, "doc_path"):
        case = compile_external_case(case.test, doc_path=case.doc_path)
    t = case.raw_case
    case_id = case.id
    request = t.get("request")
    requests = t.get("requests")
    if request is not None and requests is not None:
        raise ValueError("api.http request and requests are mutually exclusive")
    if request is None and requests is None:
        raise TypeError("api.http requires request mapping or requests list")

    h = case.harness
    mode, oauth, scenario = _parse_api_http_harness(h)
    timeout_seconds = float(h.get("timeout_seconds", 5))

    auth_mode = "none"
    oauth_token_source = "none"
    oauth_context: dict[str, Any] = {}
    if oauth is not None:
        auth_mode = "oauth"
        oauth_token_source = "env_ref"
        token_host = urllib.parse.urlparse(str(oauth["token_url"])).hostname
        oauth_context = {
            "token_url_host": token_host,
            "scope_requested": oauth.get("scope"),
            "token_fetch_ms": 0.0,
            "used_cached_token": False,
        }

    chain_state = dict(getattr(ctx, "chain_state", {}) or {})

    if request is not None:
        if not isinstance(request, dict):
            raise TypeError("api.http requires request mapping")
        request = _render_request_chain(dict(request), chain_state=chain_state)
        method, url, headers, body_bytes, _cors_req = _prepare_request(request=request)
        if oauth is not None:
            token, used_cached_token, token_fetch_ms = _oauth_access_token(
                case,
                ctx=ctx,
                oauth=oauth,
                timeout_seconds=timeout_seconds,
                mode=mode,
            )
            if not _has_header(headers, "Authorization"):
                headers["Authorization"] = f"Bearer {token}"
            oauth_context.update(
                {
                    "token_fetch_ms": token_fetch_ms,
                    "used_cached_token": used_cached_token,
                }
            )
        response = run_http_op(
            lambda: _fetch_response(
                case,
                method=method,
                url=url,
                headers=headers,
                body_bytes=body_bytes,
                timeout_seconds=timeout_seconds,
                mode=mode,
            )
        )
        body_text_value = str(response["body_text"])
        body_json_value = _json_or_none(body_text_value)
        cors_json_value = _normalize_cors(response["headers"])
        status_value = int(response["status"])
        method_value = method
        url_value = url
        steps_json_value: list[dict[str, Any]] = []
        scenario_meta: dict[str, Any] = {
            "setup_started": False,
            "setup_ready": False,
            "teardown_ran": False,
            "step_count": 1,
            "step_ids": [],
        }
    else:
        if not isinstance(requests, list) or not requests:
            raise TypeError("api.http requests must be a non-empty list")
        for idx, step in enumerate(requests):
            if not isinstance(step, dict):
                raise TypeError(f"api.http requests[{idx}] must be a mapping")
            step_id = str(step.get("id", "")).strip()
            if not step_id:
                raise ValueError(f"api.http requests[{idx}].id is required")
            requests[idx] = _render_request_chain(dict(step), chain_state=chain_state)
        scenario_cfg = scenario or {}
        final, step_results, scenario_meta, _ = _run_scenario(
            case,
            ctx=ctx,
            scenario=scenario_cfg,
            requests=[dict(x) for x in requests],
            timeout_seconds=timeout_seconds,
            mode=mode,
            oauth=oauth,
            initial_oauth_context=oauth_context,
        )
        status_value = int(final["status"])
        method_value = str(final["method"])
        url_value = str(final["url"])
        body_text_value = str(final["body_text"])
        body_json_value = final["body_json"]
        cors_json_value = final["cors_json"]
        oauth_context = dict(final.get("oauth_context") or oauth_context)
        response = {"headers": final["headers"]}
        steps_json_value = [
            {
                "id": x["id"],
                "method": x["method"],
                "url": x["url"],
                "status": x["status"],
                "headers": x["headers"],
                "body_text": x["body_text"],
                "body_json": x["body_json"],
                "cors_json": x["cors_json"],
            }
            for x in step_results
        ]

    status_text = str(status_value)
    headers_text = "\n".join(f"{k}: {v}" for k, v in sorted(response["headers"].items()))

    context_profile = {
        "profile_id": "api.http/v1",
        "profile_version": 2,
        "value": {
            "status": status_value,
            "headers": response["headers"],
            "body_text": body_text_value,
            "body_json": body_json_value,
            "cors": cors_json_value,
        },
        "meta": {
            "target": "api.http",
            "method": method_value,
            "url": url_value,
            "auth_mode": auth_mode,
            "oauth_token_source": oauth_token_source,
        },
        "context": {
            "timeout_seconds": timeout_seconds,
            "oauth": oauth_context,
            "scenario": scenario_meta,
            "steps": steps_json_value,
        },
    }

    case_key = f"{case.doc_path.resolve().as_posix()}::{case_id}"
    chain_imports = dict(ctx.get_case_chain_imports(case_key=case_key))
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    execution = build_execution_context(
        case_id=case_id,
        case_type=case.type,
        harness={**case.harness, "_chain_imports": chain_imports},
        doc_path=case.doc_path,
    )
    targets = {
        "status": status_text,
        "headers": headers_text,
        "body_text": body_text_value,
        "body_json": body_json_value,
        "cors_json": cors_json_value,
        "steps_json": steps_json_value,
        "context_json": context_profile,
        "chain_json": chain_payload,
    }
    targets["meta_json"] = build_meta_subject(
        case=case,
        ctx=ctx,
        case_key=case_key,
        harness={**case.harness, "_chain_imports": chain_imports},
        artifacts=targets,
    )
    ctx.set_case_targets(case_key=case_key, targets=targets)
    run_assertions_with_context(
        assert_tree=case.assert_tree,
        raw_assert_spec=t.get("contract", []) or [],
        raw_case=t,
        ctx=ctx,
        execution=execution,
        subject_for_key=lambda k: resolve_subject_for_target(k, targets, type_name="api.http"),
    )
