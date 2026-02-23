```yaml contract-spec
id: DCCONF-PHP-TEXT-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: text.file contain assertion passes in php bootstrap
purpose: Baseline positive contain check for the php text.file subset.
type: contract.check
expect:
  portable:
    status: pass
    category: null
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
      std.string.contains:
      - {var: text}
      - 'version: 1'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: text.file regex assertion can fail in php bootstrap
purpose: Baseline failing regex check for the php text.file subset.
type: contract.check
expect:
  portable:
    status: fail
    category: assertion
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


```yaml contract-spec
id: DCCONF-PHP-TEXT-003
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: nested must group with inherited target passes
purpose: Verifies nested must groups inherit target from parent nodes.
type: contract.check
expect:
  portable:
    status: pass
    category: null
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
      std.string.contains:
      - {var: text}
      - 'version: 1'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-004
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: can passes when at least one branch passes
purpose: Verifies can succeeds when at least one branch succeeds.
type: contract.check
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MAY
    assert:
    - std.string.regex_match:
      - {var: text}
      - (?!)
    - std.string.contains:
      - {var: text}
      - 'version: 1'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-005
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: can fails when all branches fail
purpose: Verifies can fails when every branch assertion fails.
type: contract.check
expect:
  portable:
    status: fail
    category: assertion
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MAY
    assert:
    - std.string.regex_match:
      - {var: text}
      - \A\Z
    - std.string.regex_match:
      - {var: text}
      - (?!)
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-006
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: cannot passes when all branches fail
purpose: Verifies cannot succeeds when every branch assertion fails.
type: contract.check
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MUST_NOT
    assert:
    - std.string.regex_match:
      - {var: text}
      - \A\Z
    - std.string.regex_match:
      - {var: text}
      - (?!)
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-007
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: cannot fails when any branch passes
purpose: Verifies cannot fails when at least one branch succeeds.
type: contract.check
expect:
  portable:
    status: fail
    category: assertion
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MUST_NOT
    assert:
    - std.string.contains:
      - {var: text}
      - 'version: 1'
    - std.string.regex_match:
      - {var: text}
      - (?!)
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-008
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: nested mixed groups with inherited target passes
purpose: Covers mixed nested must/may/must_not evaluation with inherited targets.
type: contract.check
expect:
  portable:
    status: pass
    category: null
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MAY
    assert:
    - std.string.regex_match:
      - {var: text}
      - \A\Z
    - std.string.contains:
      - {var: text}
      - 'version: 1'
  - id: assert_2
    class: MUST_NOT
    assert:
      std.string.regex_match:
      - {var: text}
      - \A\Z
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-009
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: evaluate regex remains pass under assert_health error mode
purpose: Confirms evaluate regex assertions bypass sugar diagnostics and can pass under error
  mode.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
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
      - '(?<=version: )1'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-010
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: evaluate empty contains remains pass under assert_health error mode
purpose: Confirms evaluate contains with empty string does not trigger sugar diagnostic failures
  in error mode.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
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
      std.string.contains:
      - {var: text}
      - ''
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-011
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: evaluate always-true regex remains pass under assert_health error mode
purpose: Confirms evaluate regex assertions are evaluated directly without sugar-level AH002
  failures.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
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
      - .*
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-012
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: evaluate duplicate contains remain pass under assert_health error mode
purpose: Confirms evaluate duplicate contains expressions do not trigger sugar-level AH003
  diagnostics.
type: contract.check
expect:
  portable:
    status: fail
    category: assertion
    message_tokens:
    - AH004
    - contract[0].asserts[0].MUST
assert_health:
  mode: error
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
    - std.string.contains:
      - {var: text}
      - 'version: 1'
    - std.string.contains:
      - {var: text}
      - 'version: 1'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-013
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: evaluate sibling branches remain pass under assert_health error mode
purpose: Confirms evaluate-only non-redundant sibling branches in can groups remain valid
  in error mode.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: error
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - text
  steps:
  - id: assert_1
    class: MAY
    assert:
    - std.string.contains:
      - {var: text}
      - 'version: 1'
    - std.string.contains:
      - {var: text}
      - 'version: 2'
harness:
  check:
    profile: text.file
    config: {}
```


```yaml contract-spec
id: DCCONF-PHP-TEXT-014
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: warn mode emits diagnostics without failing the case
purpose: Checks warn mode emits diagnostics without converting the case to failure.
type: contract.check
expect:
  portable:
    status: pass
    category: null
assert_health:
  mode: warn
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
      std.string.contains:
      - {var: text}
      - ''
harness:
  check:
    profile: text.file
    config: {}
```
