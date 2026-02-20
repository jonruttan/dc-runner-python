from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

GovernanceCheck = Callable[..., list[str] | dict[str, Any]]
GovernanceCheckMap = dict[str, GovernanceCheck]


def infer_check_domain(check_id: str) -> str:
    return str(check_id).split(".", 1)[0] if "." in str(check_id) else "misc"


def normalize_root(root: str | Path | None) -> Path:
    if root is None:
        return Path(".").resolve()
    return Path(str(root)).resolve()
