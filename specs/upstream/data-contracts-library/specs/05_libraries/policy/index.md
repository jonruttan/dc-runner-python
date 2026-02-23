# Policy Libraries Domain Index

Canonical domain index for executable specs in this subtree.

Canonical shared-library source of truth is maintained in:

- `https://github.com/jonruttan/data-contracts-library`

## Files

- `/payloads/data-contracts-library/core/specs/05_libraries/policy/policy_assertions.spec.md`
- `/payloads/data-contracts-library/core/specs/05_libraries/policy/policy_text.spec.md`
- `/payloads/data-contracts-library/core/specs/05_libraries/policy/policy_job.spec.md`

## Exported Symbols

- `policy.assert.no_violations(subject)`
- `policy.assert.summary_passed(subject)`
- `policy.assert.summary_check_id(subject, expected_check_id)`
- `policy.assert.scan_pass(subject, expected_check_id)`
- `policy.text.contains_all(text, required_tokens)`
- `policy.text.contains_none(text, forbidden_tokens)`
- `policy.text.contains_pair(text, token_a, token_b)`
- `policy.job.dispatch_ok(summary_json)`
- `policy.job.written_path_contains(summary_json, expected_path)`
- `policy.job.hooks_present(job_map)`
