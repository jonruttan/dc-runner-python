from __future__ import annotations

from pathlib import Path

from spec_runner.components.contracts import HarnessExecutionContext
from spec_runner.spec_lang import capabilities_from_harness, compile_import_bindings, limits_from_harness


def build_execution_context(*, case_id: str, case_type: str, harness: dict, doc_path) -> HarnessExecutionContext:
    limits = limits_from_harness(harness)
    imports = compile_import_bindings((harness or {}).get("spec_lang"))
    capabilities = capabilities_from_harness(harness)
    spec_lang_cfg = dict((harness or {}).get("spec_lang") or {})
    if spec_lang_cfg.get("includes"):
        raise ValueError(
            "harness.spec_lang.includes is not supported for executable cases; use harness.chain symbol exports/imports"
        )
    symbols: dict[str, object] = {}
    chain_bindings = dict((harness or {}).get("_chain_imports") or {})
    if chain_bindings:
        for key in chain_bindings:
            s = str(key).strip()
            if not s:
                raise ValueError("harness.chain.imports local binding names must be non-empty strings")
            if s in symbols:
                raise ValueError(f"harness.chain.imports local binding collides with existing symbol: {s}")
        symbols = {**symbols, **{str(k): v for k, v in chain_bindings.items()}}
    return HarnessExecutionContext(
        case_id=case_id,
        case_type=case_type,
        doc_path=Path(doc_path).as_posix(),
        limits=limits,
        imports=imports,
        symbols=symbols,
        capabilities=capabilities,
    )
