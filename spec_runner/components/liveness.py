from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ
from typing import Any, cast

from spec_runner.components.profiler import RunProfiler


_LEVEL_ORDER = {"off": 0, "basic": 1, "strict": 2}


class LivenessError(RuntimeError):
    def __init__(self, *, reason_token: str, message: str) -> None:
        super().__init__(message)
        self.reason_token = reason_token


@dataclass(frozen=True)
class LivenessConfig:
    level: str = "off"
    stall_ms: int = 30_000
    min_events: int = 1
    hard_cap_ms: int = 1_800_000
    kill_grace_ms: int = 5_000

    @property
    def enabled(self) -> bool:
        return _LEVEL_ORDER.get(self.level, 0) > 0

    @property
    def strict(self) -> bool:
        return _LEVEL_ORDER.get(self.level, 0) >= _LEVEL_ORDER["strict"]


def config_from_env(default_level: str = "off") -> LivenessConfig:
    level = str(os.environ.get("SPEC_RUNNER_LIVENESS_LEVEL", default_level)).strip().lower()
    if level not in _LEVEL_ORDER:
        level = default_level if default_level in _LEVEL_ORDER else "off"

    def _env_pos_int(name: str, default: int) -> int:
        raw = str(os.environ.get(name, "")).strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            return default
        return value if value > 0 else default

    return LivenessConfig(
        level=level,
        stall_ms=_env_pos_int("SPEC_RUNNER_LIVENESS_STALL_MS", 30_000),
        min_events=_env_pos_int("SPEC_RUNNER_LIVENESS_MIN_EVENTS", 1),
        hard_cap_ms=_env_pos_int("SPEC_RUNNER_LIVENESS_HARD_CAP_MS", 1_800_000),
        kill_grace_ms=_env_pos_int("SPEC_RUNNER_LIVENESS_KILL_GRACE_MS", 5_000),
    )


def _kill_process_tree(proc: subprocess.Popen[bytes], *, grace_ms: int) -> None:
    try:
        pgid = os.getpgid(proc.pid)
    except Exception:  # noqa: BLE001
        pgid = None
    try:
        if pgid is not None:
            os.killpg(pgid, signal.SIGTERM)
        else:
            proc.terminate()
    except Exception:  # noqa: BLE001
        pass
    deadline = time.monotonic() + (max(grace_ms, 1) / 1000.0)
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.05)
    try:
        if pgid is not None:
            os.killpg(pgid, signal.SIGKILL)
        else:
            proc.kill()
    except Exception:  # noqa: BLE001
        pass


def run_subprocess_with_liveness(
    *,
    command: list[str],
    cwd: Path,
    profiler: RunProfiler | None,
    phase: str,
    cfg: LivenessConfig,
) -> subprocess.CompletedProcess[str]:
    span_id: str | None = None
    if profiler is not None and profiler.cfg.enabled:
        span_ctx = profiler.span(
            name="subprocess.exec",
            kind="subprocess",
            phase=phase,
            attrs={"argv_count": len(command), "cwd": str(cwd)},
        )
    else:
        span_ctx = None

    if span_ctx is None:
        # Fallback path without profiling context manager.
        return subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
        )

    with span_ctx as sid:
        span_id = sid
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            start_new_session=True,
        )
        if profiler is not None and profiler.cfg.enabled:
            profiler.event(
                kind="subprocess_state",
                span_id=span_id,
                attrs={"state": "spawned", "pid": int(proc.pid)},
            )

        selector = DefaultSelector()
        if proc.stdout is not None:
            selector.register(proc.stdout, EVENT_READ, data="stdout")
        if proc.stderr is not None:
            selector.register(proc.stderr, EVENT_READ, data="stderr")

        start_ns = time.monotonic_ns()
        last_progress_ns = start_ns
        event_times_ns: list[int] = [start_ns]
        out_chunks: list[bytes] = []
        err_chunks: list[bytes] = []

        while True:
            now_ns = time.monotonic_ns()
            elapsed_ms = (now_ns - start_ns) / 1_000_000.0
            idle_ms = (now_ns - last_progress_ns) / 1_000_000.0

            # Keep only events within the configured stall window.
            stall_window_ns = max(int(cfg.stall_ms), 1) * 1_000_000
            event_times_ns = [t for t in event_times_ns if (now_ns - t) <= stall_window_ns]

            if cfg.enabled and cfg.hard_cap_ms > 0 and elapsed_ms > float(cfg.hard_cap_ms):
                if profiler is not None and profiler.cfg.enabled:
                    profiler.note_timeout(
                        reason_token="timeout.hard_cap.emergency",
                        span_id=span_id,
                        attrs={"elapsed_ms": round(elapsed_ms, 3), "hard_cap_ms": int(cfg.hard_cap_ms)},
                    )
                    profiler.event(
                        kind="watchdog",
                        span_id=span_id,
                        attrs={"reason_token": "watchdog.kill.term", "pid": int(proc.pid)},
                    )
                _kill_process_tree(proc, grace_ms=cfg.kill_grace_ms)
                if profiler is not None and profiler.cfg.enabled:
                    profiler.event(
                        kind="watchdog",
                        span_id=span_id,
                        attrs={"reason_token": "watchdog.kill.killed", "pid": int(proc.pid)},
                    )
                raise LivenessError(
                    reason_token="timeout.hard_cap.emergency",
                    message=f"{' '.join(command)} exceeded hard cap of {cfg.hard_cap_ms}ms",
                )

            if cfg.strict and cfg.stall_ms > 0 and idle_ms > float(cfg.stall_ms):
                if len(event_times_ns) < max(int(cfg.min_events), 1):
                    if profiler is not None and profiler.cfg.enabled:
                        profiler.note_timeout(
                            reason_token="stall.subprocess.no_output_no_event",
                            span_id=span_id,
                            attrs={"idle_ms": round(idle_ms, 3), "stall_ms": int(cfg.stall_ms)},
                        )
                        profiler.event(
                            kind="watchdog",
                            span_id=span_id,
                            attrs={"reason_token": "watchdog.kill.term", "pid": int(proc.pid)},
                        )
                    _kill_process_tree(proc, grace_ms=cfg.kill_grace_ms)
                    if profiler is not None and profiler.cfg.enabled:
                        profiler.event(
                            kind="watchdog",
                            span_id=span_id,
                            attrs={"reason_token": "watchdog.kill.killed", "pid": int(proc.pid)},
                        )
                    raise LivenessError(
                        reason_token="stall.subprocess.no_output_no_event",
                        message=f"{' '.join(command)} made no progress for {cfg.stall_ms}ms",
                    )

            had_io = False
            for key, _ in selector.select(timeout=0.2):
                stream_name = str(key.data)
                file_obj = key.fileobj
                if isinstance(file_obj, int):
                    continue
                readable_obj = cast(Any, file_obj)
                if hasattr(file_obj, "read1"):
                    chunk = readable_obj.read1(4096)
                else:
                    chunk = readable_obj.read(4096)
                if not chunk:
                    try:
                        selector.unregister(file_obj)
                    except Exception:  # noqa: BLE001
                        pass
                    continue
                had_io = True
                if stream_name == "stdout":
                    out_chunks.append(chunk)
                else:
                    err_chunks.append(chunk)
                last_progress_ns = time.monotonic_ns()
                event_times_ns.append(last_progress_ns)
                if profiler is not None and profiler.cfg.enabled:
                    profiler.event(
                        kind="io.read",
                        span_id=span_id,
                        attrs={"stream": stream_name, "bytes": len(chunk)},
                    )

            if not had_io:
                if proc.poll() is not None and not selector.get_map():
                    break
            else:
                # Ensure process exit is observed when pipes were active.
                if proc.poll() is not None and not selector.get_map():
                    break

        returncode = int(proc.wait())
        if profiler is not None and profiler.cfg.enabled:
            profiler.event(
                kind="subprocess_state",
                span_id=span_id,
                attrs={"state": "exit", "returncode": returncode, "pid": int(proc.pid)},
            )
        stdout_text = b"".join(out_chunks).decode("utf-8", errors="replace")
        stderr_text = b"".join(err_chunks).decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(command, returncode, stdout_text, stderr_text)
