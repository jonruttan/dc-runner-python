# Failure Context Conformance Cases

These fixtures ensure assertion failures expose stable context tokens so
debugging and parity checks remain deterministic.

## DCCONF-ERR-001

```yaml contract-spec
id: DCCONF-ERR-001
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
