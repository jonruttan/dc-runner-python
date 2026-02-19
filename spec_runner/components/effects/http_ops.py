from __future__ import annotations

from typing import Any, Callable


def run_http_op(op: Callable[[], Any]) -> Any:
    return op()

