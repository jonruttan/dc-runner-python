from __future__ import annotations

from typing import Any, Mapping


def resolve_subject_for_target(subject_key: str, mapping: Mapping[str, Any], *, type_name: str) -> Any:
    if subject_key not in mapping:
        raise ValueError(f"unknown assert target for {type_name}: {subject_key}")
    return mapping[subject_key]

