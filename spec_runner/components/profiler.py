from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping


_LEVEL_ORDER = {"off": 0, "basic": 1, "detailed": 2, "debug": 3}
_REDACT_ATTR_TOKENS = ("token", "secret", "password", "authorization", "cookie", "key")


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_level(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if value in _LEVEL_ORDER:
        return value
    return "off"


def _env_int(name: str, default: int) -> int:
    raw = str(os.environ.get(name, "")).strip()
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        return default
    return val if val > 0 else default


def _redact_value(value: Any) -> Any:
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    text = str(value)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"<redacted:{digest}>"


def _sanitize_attrs(attrs: Mapping[str, Any] | None) -> dict[str, Any]:
    if not attrs:
        return {}
    out: dict[str, Any] = {}
    for k, v in attrs.items():
        key = str(k).strip()
        if not key:
            continue
        low = key.lower()
        if any(tok in low for tok in _REDACT_ATTR_TOKENS):
            out[key] = _redact_value(v)
            continue
        if isinstance(v, Mapping):
            out[key] = _sanitize_attrs(v)
            continue
        if isinstance(v, list):
            out[key] = [_redact_value(x) for x in v]
            continue
        out[key] = v
    return out


def env_profile_snapshot(env: Mapping[str, str] | None) -> dict[str, Any]:
    if not env:
        return {}
    keys = sorted(str(k) for k in env.keys())
    profile: dict[str, Any] = {}
    for key in keys:
        val = env.get(key)
        profile[key] = {
            "set": bool(val),
            "length": len(val) if isinstance(val, str) else 0,
            "sha256_12": hashlib.sha256(str(val or "").encode("utf-8")).hexdigest()[:12] if val else "",
        }
    return profile


@dataclass(frozen=True)
class ProfileConfig:
    level: str = "off"
    out_path: str = "/.artifacts/run-trace.json"
    summary_out_path: str = "/.artifacts/run-trace-summary.md"
    heartbeat_ms: int = 1000
    stall_threshold_ms: int = 10000
    runner_impl: str = "python"
    command: str = ""
    args: list[str] | None = None
    env: Mapping[str, str] | None = None

    @property
    def enabled(self) -> bool:
        return _LEVEL_ORDER.get(self.level, 0) > 0


class RunProfiler:
    def __init__(self, cfg: ProfileConfig) -> None:
        self.cfg = cfg
        self._lock = threading.RLock()
        self._counter = 0
        self._spans: list[dict[str, Any]] = []
        self._events: list[dict[str, Any]] = []
        self._closed = False
        self._heartbeat_stop = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        self._last_progress_ns = time.monotonic_ns()
        self._stall_emitted = False
        self.run_id = f"run-{int(time.time() * 1000)}"
        self.started_at = _iso_utc_now()
        self.start_ns = time.monotonic_ns()
        self._run_total_span_id: str | None = None

        if self.cfg.enabled:
            self._run_total_span_id = self._start_span(
                name="run.total",
                kind="run",
                phase="run.total",
                parent_span_id=None,
                attrs={"runner_impl": self.cfg.runner_impl},
            )
            if _LEVEL_ORDER.get(self.cfg.level, 0) >= _LEVEL_ORDER["detailed"]:
                self._start_heartbeat()

    def _next_span_id(self) -> str:
        self._counter += 1
        return f"s{self._counter}"

    def _mark_progress(self) -> None:
        self._last_progress_ns = time.monotonic_ns()

    def _start_span(
        self,
        *,
        name: str,
        kind: str,
        phase: str,
        parent_span_id: str | None,
        attrs: Mapping[str, Any] | None,
    ) -> str:
        sid = self._next_span_id()
        now_ns = time.monotonic_ns()
        span = {
            "span_id": sid,
            "parent_span_id": parent_span_id,
            "kind": str(kind),
            "name": str(name),
            "phase": str(phase),
            "start_ns": int(now_ns),
            "end_ns": None,
            "duration_ms": None,
            "status": "ok",
            "attrs": _sanitize_attrs(attrs),
            "error": None,
        }
        self._spans.append(span)
        self._mark_progress()
        return sid

    def _finish_span(
        self,
        span_id: str,
        *,
        status: str = "ok",
        error: Mapping[str, Any] | None = None,
    ) -> None:
        now_ns = time.monotonic_ns()
        for span in reversed(self._spans):
            if span.get("span_id") != span_id:
                continue
            if span.get("end_ns") is not None:
                return
            span["end_ns"] = int(now_ns)
            span["duration_ms"] = round((now_ns - int(span["start_ns"])) / 1_000_000.0, 3)
            span["status"] = status
            span["error"] = _sanitize_attrs(error)
            self._mark_progress()
            return

    @contextlib.contextmanager
    def span(
        self,
        *,
        name: str,
        kind: str,
        phase: str,
        parent_span_id: str | None = None,
        attrs: Mapping[str, Any] | None = None,
    ) -> Iterator[str | None]:
        if not self.cfg.enabled:
            yield None
            return
        with self._lock:
            sid = self._start_span(
                name=name,
                kind=kind,
                phase=phase,
                parent_span_id=parent_span_id,
                attrs=attrs,
            )
        try:
            yield sid
        except BaseException as exc:  # noqa: BLE001
            with self._lock:
                self._finish_span(
                    sid,
                    status="error",
                    error={"category": "runtime", "message": str(exc)},
                )
            raise
        else:
            with self._lock:
                self._finish_span(sid, status="ok")

    def event(self, *, kind: str, span_id: str | None = None, attrs: Mapping[str, Any] | None = None) -> None:
        if not self.cfg.enabled:
            return
        with self._lock:
            self._events.append(
                {
                    "ts_ns": int(time.monotonic_ns()),
                    "kind": str(kind),
                    "span_id": span_id,
                    "attrs": _sanitize_attrs(attrs),
                }
            )
            self._mark_progress()

    def note_timeout(self, *, reason_token: str, span_id: str | None = None, attrs: Mapping[str, Any] | None = None) -> None:
        merged = dict(attrs or {})
        merged["reason_token"] = reason_token
        self.event(kind="watchdog", span_id=span_id, attrs=merged)

    def _start_heartbeat(self) -> None:
        if self._heartbeat_thread is not None:
            return

        def _run() -> None:
            beat_s = max(self.cfg.heartbeat_ms, 1) / 1000.0
            stall_ns = max(self.cfg.stall_threshold_ms, 1) * 1_000_000
            while not self._heartbeat_stop.wait(beat_s):
                now_ns = time.monotonic_ns()
                with self._lock:
                    delta_ns = now_ns - self._last_progress_ns
                    self._events.append(
                        {
                            "ts_ns": int(now_ns),
                            "kind": "heartbeat",
                            "span_id": self._run_total_span_id,
                            "attrs": {"idle_ms": round(delta_ns / 1_000_000.0, 3)},
                        }
                    )
                    if delta_ns > stall_ns and not self._stall_emitted:
                        self._events.append(
                            {
                                "ts_ns": int(now_ns),
                                "kind": "stall_warning",
                                "span_id": self._run_total_span_id,
                                "attrs": {
                                    "idle_ms": round(delta_ns / 1_000_000.0, 3),
                                    "threshold_ms": int(self.cfg.stall_threshold_ms),
                                },
                            }
                        )
                        self._events.append(
                            {
                                "ts_ns": int(now_ns),
                                "kind": "watchdog",
                                "span_id": self._run_total_span_id,
                                "attrs": {"reason_token": "stall.runner.no_progress"},
                            }
                        )
                        self._stall_emitted = True

        self._heartbeat_thread = threading.Thread(target=_run, name="spec-runner-profiler-heartbeat", daemon=True)
        self._heartbeat_thread.start()

    def subprocess_run(
        self,
        *,
        command: list[str],
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
        text: bool = True,
        capture_output: bool = True,
        check: bool = False,
        parent_span_id: str | None = None,
        phase: str = "subprocess.exec",
    ) -> subprocess.CompletedProcess[Any]:
        argv = [str(x) for x in command]
        if not argv:
            raise ValueError("subprocess_run requires non-empty command")
        if not self.cfg.enabled:
            return subprocess.run(
                argv,
                cwd=None if cwd is None else str(cwd),
                env=None if env is None else dict(env),
                timeout=timeout,
                text=text,
                capture_output=capture_output,
                check=check,
            )

        with self.span(
            name="subprocess.exec",
            kind="subprocess",
            phase=phase,
            parent_span_id=parent_span_id,
            attrs={
                "argv_hash": hashlib.sha256(" ".join(argv).encode("utf-8")).hexdigest()[:12],
                "cwd": None if cwd is None else str(cwd),
                "timeout_ms": None if timeout is None else int(float(timeout) * 1000.0),
            },
        ) as exec_span_id:
            stdout_pipe = subprocess.PIPE if capture_output else None
            stderr_pipe = subprocess.PIPE if capture_output else None
            proc = subprocess.Popen(
                argv,
                cwd=None if cwd is None else str(cwd),
                env=None if env is None else dict(env),
                stdout=stdout_pipe,
                stderr=stderr_pipe,
                text=text,
            )
            self.event(
                kind="subprocess_state",
                span_id=exec_span_id,
                attrs={"state": "spawned", "pid": int(proc.pid)},
            )
            with self.span(
                name="subprocess.wait",
                kind="subprocess",
                phase="subprocess.wait",
                parent_span_id=exec_span_id,
                attrs={"pid": int(proc.pid)},
            ) as wait_span_id:
                try:
                    out, err = proc.communicate(timeout=timeout)
                except subprocess.TimeoutExpired as exc:
                    self.event(
                        kind="subprocess_state",
                        span_id=wait_span_id,
                        attrs={"state": "timeout", "timeout_s": float(timeout or 0.0)},
                    )
                    self.note_timeout(
                        reason_token="timeout.subprocess.wait",
                        span_id=wait_span_id,
                        attrs={"pid": int(proc.pid)},
                    )
                    proc.kill()
                    self.event(kind="subprocess_state", span_id=wait_span_id, attrs={"state": "killed", "pid": int(proc.pid)})
                    try:
                        out, err = proc.communicate(timeout=2)
                    except Exception:  # noqa: BLE001
                        out, err = None, None
                    raise subprocess.TimeoutExpired(argv, float(timeout or 0.0), output=out, stderr=err) from exc
            if capture_output:
                self.event(
                    kind="io.read",
                    span_id=exec_span_id,
                    attrs={"stream": "stdout", "bytes": len((out or "").encode("utf-8")) if text else len(out or b"")},
                )
                self.event(
                    kind="io.read",
                    span_id=exec_span_id,
                    attrs={"stream": "stderr", "bytes": len((err or "").encode("utf-8")) if text else len(err or b"")},
                )
            self.event(
                kind="subprocess_state",
                span_id=exec_span_id,
                attrs={"state": "exit", "returncode": int(proc.returncode)},
            )
            cp = subprocess.CompletedProcess(argv, int(proc.returncode), out if capture_output else None, err if capture_output else None)
            if check and cp.returncode != 0:
                raise subprocess.CalledProcessError(
                    cp.returncode,
                    cp.args,
                    output=cp.stdout,
                    stderr=cp.stderr,
                )
            return cp

    def _summary(self, *, status: str) -> dict[str, Any]:
        spans = [s for s in self._spans if s.get("duration_ms") is not None]
        spans_sorted = sorted(spans, key=lambda x: float(x.get("duration_ms") or 0.0), reverse=True)
        timeout_spans = [s for s in spans if str(s.get("status")) == "timeout"]
        stall_events = [e for e in self._events if str(e.get("kind")) == "stall_warning"]
        return {
            "span_count": len(self._spans),
            "event_count": len(self._events),
            "status": status,
            "slowest_spans": [
                {
                    "span_id": s.get("span_id"),
                    "name": s.get("name"),
                    "phase": s.get("phase"),
                    "duration_ms": s.get("duration_ms"),
                    "status": s.get("status"),
                }
                for s in spans_sorted[:20]
            ],
            "timeout_span_count": len(timeout_spans),
            "stall_warning_count": len(stall_events),
            "last_progress_event": self._events[-1] if self._events else None,
        }

    def render_summary_markdown(self, *, status: str) -> str:
        summary = self._summary(status=status)
        lines = [
            "# Run Trace Summary",
            "",
            f"- run_id: `{self.run_id}`",
            f"- status: `{status}`",
            f"- runner_impl: `{self.cfg.runner_impl}`",
            f"- span_count: `{summary['span_count']}`",
            f"- event_count: `{summary['event_count']}`",
            f"- timeout_span_count: `{summary['timeout_span_count']}`",
            f"- stall_warning_count: `{summary['stall_warning_count']}`",
            "",
            "## Slowest Spans",
            "",
            "| span_id | name | phase | status | duration_ms |",
            "|---|---|---|---|---|",
        ]
        for row in summary["slowest_spans"]:
            lines.append(
                f"| `{row.get('span_id','')}` | `{row.get('name','')}` | `{row.get('phase','')}` | `{row.get('status','')}` | `{row.get('duration_ms','')}` |"
            )
        if not summary["slowest_spans"]:
            lines.append("| - | - | - | - | - |")
        lines += [
            "",
            "## Timeout/Stall Chain",
            "",
            f"- last_progress_event: `{json.dumps(summary.get('last_progress_event') or {}, sort_keys=True)}`",
            "",
            "## Suggested Next Command",
            "",
            "- rerun with `--profile-level debug --profile-heartbeat-ms 250 --profile-stall-threshold-ms 2000`",
            "",
        ]
        return "\n".join(lines)

    def close(
        self,
        *,
        status: str,
        out_path: Path,
        summary_out_path: Path,
        exit_code: int | None = None,
    ) -> None:
        if not self.cfg.enabled or self._closed:
            return
        self._closed = True
        self._heartbeat_stop.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=1.0)

        with self._lock:
            if self._run_total_span_id is not None:
                self._finish_span(self._run_total_span_id, status=status)
            payload = {
                "version": 1,
                "run_id": self.run_id,
                "runner_impl": self.cfg.runner_impl,
                "started_at": self.started_at,
                "ended_at": _iso_utc_now(),
                "status": status,
                "exit_code": exit_code,
                "command": self.cfg.command,
                "args": list(self.cfg.args or []),
                "env_profile": env_profile_snapshot(self.cfg.env),
                "spans": self._spans,
                "events": self._events,
                "summary": self._summary(status=status),
            }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary_out_path.parent.mkdir(parents=True, exist_ok=True)
        summary_out_path.write_text(self.render_summary_markdown(status=status), encoding="utf-8")


def profile_config_from_args(
    *,
    profile_level: str | None,
    profile_out: str | None,
    profile_summary_out: str | None,
    profile_heartbeat_ms: int | None,
    profile_stall_threshold_ms: int | None,
    runner_impl: str,
    command: str,
    args: list[str],
    env: Mapping[str, str] | None = None,
) -> ProfileConfig:
    level = _to_level(
        str(profile_level or "").strip() or os.environ.get("SPEC_RUNNER_PROFILE_LEVEL", "off")
    )
    out_path = str(profile_out or "").strip() or os.environ.get("SPEC_RUNNER_PROFILE_OUT", "/.artifacts/run-trace.json")
    summary_out_path = str(profile_summary_out or "").strip() or os.environ.get(
        "SPEC_RUNNER_PROFILE_SUMMARY_OUT",
        "/.artifacts/run-trace-summary.md",
    )
    heartbeat_ms = (
        int(profile_heartbeat_ms)
        if isinstance(profile_heartbeat_ms, int) and profile_heartbeat_ms > 0
        else _env_int("SPEC_RUNNER_PROFILE_HEARTBEAT_MS", 1000)
    )
    stall_threshold_ms = (
        int(profile_stall_threshold_ms)
        if isinstance(profile_stall_threshold_ms, int) and profile_stall_threshold_ms > 0
        else _env_int("SPEC_RUNNER_PROFILE_STALL_THRESHOLD_MS", 10000)
    )
    return ProfileConfig(
        level=level,
        out_path=out_path,
        summary_out_path=summary_out_path,
        heartbeat_ms=heartbeat_ms,
        stall_threshold_ms=stall_threshold_ms,
        runner_impl=runner_impl,
        command=command,
        args=list(args),
        env=env,
    )
