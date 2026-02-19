from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from spec_runner.spec_lang import SpecLangLimits


@dataclass(frozen=True)
class HarnessExecutionContext:
    case_id: str
    case_type: str
    doc_path: str
    limits: SpecLangLimits
    imports: Mapping[str, str]
    symbols: Mapping[str, Any]
    capabilities: frozenset[str]
