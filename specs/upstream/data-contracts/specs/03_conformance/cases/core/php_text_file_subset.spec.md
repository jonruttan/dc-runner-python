```yaml contract-spec
spec_version: 1
schema_ref: "/specs/01_schema/schema_v1.md"
harness:
  type: unit.test
  profile: check
contracts:
  clauses:
  - id: DCCONF-PHP-TEXT-001
    title: text.file contain assertion passes in php bootstrap
    purpose: Baseline positive contain check for the php text.file subset.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - 'version: 1'
  - id: DCCONF-PHP-TEXT-002
    title: text.file regex assertion can fail in php bootstrap
    purpose: Baseline failing regex check for the php text.file subset.
    expect:
      portable:
        status: fail
        category: assertion
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
          - "\\A\\Z"
  - id: DCCONF-PHP-TEXT-003
    title: nested must group with inherited target passes
    purpose: Verifies nested must groups inherit target from parent nodes.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - 'version: 1'
  - id: DCCONF-PHP-TEXT-004
    title: can passes when at least one branch passes
    purpose: Verifies can succeeds when at least one branch succeeds.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        required: false
        assert:
        - std.string.regex_match:
          - var: text
          - "(?!)"
        - std.string.contains:
          - var: text
          - 'version: 1'
  - id: DCCONF-PHP-TEXT-005
    title: can fails when all branches fail
    purpose: Verifies can fails when every branch assertion fails.
    expect:
      portable:
        status: fail
        category: assertion
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        required: false
        assert:
        - std.string.regex_match:
          - var: text
          - "\\A\\Z"
        - std.string.regex_match:
          - var: text
          - "(?!)"
  - id: DCCONF-PHP-TEXT-006
    title: cannot passes when all branches fail
    purpose: Verifies cannot succeeds when every branch assertion fails.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.not:
          - std.logic.or:
            - std.string.regex_match:
              - var: text
              - "\\A\\Z"
            - std.string.regex_match:
              - var: text
              - "(?!)"
  - id: DCCONF-PHP-TEXT-007
    title: cannot fails when any branch passes
    purpose: Verifies cannot fails when at least one branch succeeds.
    expect:
      portable:
        status: fail
        category: assertion
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.logic.not:
          - std.logic.or:
            - std.string.contains:
              - var: text
              - 'version: 1'
            - std.string.regex_match:
              - var: text
              - "(?!)"
  - id: DCCONF-PHP-TEXT-008
    title: nested mixed groups with inherited target passes
    purpose: Covers mixed nested must/may/must_not evaluation with inherited targets.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        required: false
        assert:
        - std.string.regex_match:
          - var: text
          - "\\A\\Z"
        - std.string.contains:
          - var: text
          - 'version: 1'
      - id: assert_2
        assert:
          std.logic.not:
          - std.string.regex_match:
            - var: text
            - "\\A\\Z"
  - id: DCCONF-PHP-TEXT-009
    title: evaluate regex remains pass
    purpose: Confirms evaluate regex assertions can pass on the baseline text fixture.
    expect:
      portable:
        status: pass
        category:
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
          - "(?<=version: )1"
  - id: DCCONF-PHP-TEXT-010
    title: evaluate empty contains remains pass
    purpose: Confirms evaluate contains with an empty string passes.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - ''
  - id: DCCONF-PHP-TEXT-011
    title: evaluate always-true regex remains pass
    purpose: Confirms evaluate regex assertions are evaluated directly.
    expect:
      portable:
        status: pass
        category:
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
          - ".*"
  - id: DCCONF-PHP-TEXT-012
    title: mixed contains with unmet sibling fails assertion
    purpose: Confirms sibling contains predicates fail when one branch does not match.
    expect:
      portable:
        status: fail
        category: assertion
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - std.string.contains:
          - var: text
          - 'version: 2'
  - id: DCCONF-PHP-TEXT-013
    title: evaluate sibling branches remain pass
    purpose: Confirms evaluate-only non-redundant sibling branches remain valid.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        required: false
        assert:
        - std.string.contains:
          - var: text
          - 'version: 1'
        - std.string.contains:
          - var: text
          - 'version: 2'
  - id: DCCONF-PHP-TEXT-014
    title: empty contains baseline remains pass
    purpose: Confirms baseline contains behavior remains pass for this fixture.
    expect:
      portable:
        status: pass
        category:
    asserts:
      imports:
      - from: asset
        names:
        - text
      checks:
      - id: assert_1
        assert:
          std.string.contains:
          - var: text
          - ''
adapters:
- type: io.fs
  actions:
  - id: svc.assert_check.text_file.1
    direction: input
    profile: read.text
services:
- id: svc.assert_check.text_file.1
  consumes:
  - svc.assert_check.text_file.1
```
























