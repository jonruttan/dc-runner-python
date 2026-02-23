# Purpose Warning Codes

Stable warning codes emitted by `conformance_purpose_report.py`.

- `PUR001`: purpose duplicates title
  - default severity: `warn`
  - hint: Rewrite purpose to explain intent or risk not already stated in title.
  - suggested_edit template: Rewrite `purpose` to state intent or risk not already present in `title`.
- `PUR002`: purpose word count below minimum
  - default severity: `warn`
  - hint: Expand purpose to meet the configured minimum word count.
  - suggested_edit template: Expand `purpose` with concrete behavior intent to at least `<min_words>` words.
- `PUR003`: purpose contains placeholder token
  - default severity: `warn`
  - hint: Replace placeholder tokens with concrete, implementation-neutral intent.
  - suggested_edit template: Replace placeholder tokens with concrete, implementation-neutral intent text.
- `PUR004`: purpose lint configuration/policy error
  - default severity: `error`
  - hint: Fix purpose_lint settings or policy file shape/version before rerunning.
  - suggested_edit template: Fix `purpose_lint` configuration or policy schema/version before rerunning.
