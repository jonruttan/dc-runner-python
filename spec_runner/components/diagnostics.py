from __future__ import annotations


def schema_error(message: str) -> ValueError:
    return ValueError(message)


def runtime_error(message: str) -> RuntimeError:
    return RuntimeError(message)

