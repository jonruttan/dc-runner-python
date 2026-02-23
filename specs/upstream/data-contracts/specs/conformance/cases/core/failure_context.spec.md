These fixtures ensure assertion failures expose stable context tokens so
debugging and parity checks remain deterministic.


```yaml contract-spec
id: DCCONF-ERR-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: failing assertion includes context tokens in message
purpose: Guarantees failure messages carry deterministic context tokens for debugging and
  parity.
type: contract.check
expect:
  portable:
    status: fail
    category: assertion
    message_tokens:
    - case_id=DCCONF-ERR-001
    - contract_path=contract[0]
    - target=text
    - op=evaluate
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    assert:
      std.string.regex_match:
      - {var: text}
      - \A\Z
harness:
  check:
    profile: text.file
    config: {}
```
