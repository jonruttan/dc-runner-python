from __future__ import annotations

import subprocess
from pathlib import Path


def run_process_op(
    *,
    command: list[str],
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    timeout: float | None = None,
    profiler: object | None = None,
    phase: str = "subprocess.exec",
) -> subprocess.CompletedProcess[str]:
    if profiler is not None and hasattr(profiler, "subprocess_run"):
        return profiler.subprocess_run(
            command=command,
            cwd=cwd,
            env=env,
            check=check,
            timeout=timeout,
            text=True,
            capture_output=True,
            phase=phase,
        )
    return subprocess.run(
        [str(x) for x in command],
        cwd=None if cwd is None else str(cwd),
        env=env,
        check=check,
        timeout=timeout,
        capture_output=True,
        text=True,
    )
