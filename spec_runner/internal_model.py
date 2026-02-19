from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class PredicateLeaf:
    op: str
    expr: Any
    assert_path: str
    target: str | None = None
    subject_key: str | None = None
    imports: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class GroupNode:
    op: Literal["MUST", "MAY", "MUST_NOT"]
    target: str | None
    children: list["InternalAssertNode"]
    assert_path: str


InternalAssertNode = GroupNode | PredicateLeaf


@dataclass(frozen=True)
class InternalSpecCase:
    id: str
    type: str
    title: str | None
    doc_path: Path
    harness: dict[str, Any]
    metadata: dict[str, Any]
    raw_case: dict[str, Any]
    assert_tree: InternalAssertNode
