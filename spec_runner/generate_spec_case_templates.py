#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json
from spec_runner.docs_template_engine import render_moustache


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    return repo_root / str(raw).lstrip("/")


def _template_payload() -> dict[str, Any]:
    contract_check = """id: EX-TEMPLATE-CHECK-001
title: canonical full contract.check template
purpose: Replace harness profile/config and assertions for your surface.
type: contract.check
doc:
  summary: Canonical full contract.check template.
  description: Author-facing baseline shape for check cases.
  audience: author
  since: v1
harness:
  root: .
  check:
    profile: governance.scan
    config:
      check: docs.make_commands_sync
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  - from: artifact
    names:
    - summary_json
  steps:
  - id: assert_violation_count_zero
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
  - id: assert_summary_shape
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - passed
      - true
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - check_id
      - docs.make_commands_sync"""

    contract_job = """id: EX-TEMPLATE-JOB-001
title: canonical full contract.job template
type: contract.job
doc:
  summary: Canonical full contract.job template.
  description: Author-facing baseline shape for job-dispatch cases.
  audience: author
  since: v1
harness:
  spec_lang:
    capabilities:
    - ops.job
  jobs:
    main:
      helper: helper.docs.generate_all
      mode: custom
      inputs: {}
    on_fail:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/EX-TEMPLATE-JOB-001.fail.json
        format: json
        report_name: EX-TEMPLATE-JOB-001.fail
    on_complete:
      helper: helper.report.emit
      mode: report
      inputs:
        out: .artifacts/job-hooks/EX-TEMPLATE-JOB-001.complete.json
        format: json
        report_name: EX-TEMPLATE-JOB-001.complete
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - summary_json
  steps:
  - id: dispatch_main
    assert:
    - ops.job.dispatch:
      - main
    - std.logic.eq:
      - std.object.get:
        - {var: summary_json}
        - ok
      - true
when:
  fail:
  - ops.job.dispatch:
    - on_fail
  complete:
  - ops.job.dispatch:
    - on_complete"""

    contract_export = """id: EX-TEMPLATE-EXPORT-001
title: canonical full contract.export template
type: contract.export
domain: example
doc:
  summary: Canonical full contract.export template.
  description: Author-facing baseline shape for exported assertion functions.
  audience: author
  since: v1
library:
  id: example.core
  module: example
  stability: alpha
  owner: spec_runner
harness:
  exports:
  - as: example.symbol
    from: assert.function
    path: /assert_symbol
    params:
    - subject
    doc:
      summary: One-sentence symbol summary.
      description: Concise symbol description and intended usage.
      params:
      - name: subject
        type: any
        required: true
        description: Input under evaluation.
      returns:
        type: bool
        description: True when assertion passes.
      errors:
      - code: ASSERT_SYMBOL_ERROR
        when: Evaluation fails or payload is malformed.
        category: assertion
      examples:
      - title: subject contains required token
        input: '{"subject": "hello"}'
        expected: true
      portability:
        python: true
        php: true
        rust: true
      since: v1
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - subject
  steps:
  - id: assert_symbol
    assert:
      std.string.contains:
      - {var: subject}
      - hello"""

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "contract_check": contract_check,
        "contract_job": contract_job,
        "contract_export": contract_export,
    }


def _render_md(payload: dict[str, Any], *, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {"templates": payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate canonical full spec case templates reference page.")
    ap.add_argument("--out", default=".artifacts/spec-case-templates.json")
    ap.add_argument("--doc-out", default="docs/book/93n_spec_case_templates_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _template_payload()

    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    template_path = repo_root / "docs/book/templates/spec_case_templates_reference_template.md"

    md_block = _render_md(payload, template_path=template_path)
    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="spec_case_templates_reference",
        body=md_block,
    )

    if ns.check:
        if parse_generated_block(
            doc_path.read_text(encoding="utf-8"),
            surface_id="spec_case_templates_reference",
        ).strip() != md_block.strip():
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
