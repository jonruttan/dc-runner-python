These fixtures ensure assertion failures expose stable context tokens so
debugging and parity checks remain deterministic.


```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-ERR-001
    title: failing assertion includes context tokens in message
    purpose: Guarantees failure messages carry deterministic context tokens for debugging
      and parity.
    expect:
      portable:
        status: fail
        category: assertion
        message_tokens:
        - case_id=DCCONF-ERR-001
        - contract_path=contract[0]
        - target=text
        - op=evaluate
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.regex_match:
          - var: text
          - \A\Z
adapters:
- type: io.fs
  actions:
  - id: svc.check.text_file.1
    direction: input
    profile: read.text
services:
- id: svc.check.text_file.1
  consumes:
  - svc.check.text_file.1
```
