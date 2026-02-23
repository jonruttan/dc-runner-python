# Text Policy Library

## LIB-POLICY-TEXT-001

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    exports:
    - as: policy.text.contains_all
      from: assert.function
      path: /__export__policy.text.contains_all
      params:
      - text
      - required_tokens
      required: true
    - as: policy.text.contains_none
      from: assert.function
      path: /__export__policy.text.contains_none
      params:
      - text
      - forbidden_tokens
      required: true
    - as: policy.text.contains_pair
      from: assert.function
      path: /__export__policy.text.contains_pair
      params:
      - text
      - token_a
      - token_b
      required: true
contracts:
  clauses:
  - id: LIB-POLICY-TEXT-001
    title: reusable text token assertions
    library:
      id: policy.text
      module: policy
      stability: alpha
      owner: data-contracts-library
      tags:
      - policy
      - text
    asserts:
      checks:
      - id: __export__policy.text.contains_all
        assert:
          std.array.all:
          - var: required_tokens
          - fn:
              params:
              - token
              body:
                std.string.contains:
                - var: text
                - var: token
        required: true
      - id: __export__policy.text.contains_none
        assert:
          std.array.all:
          - var: forbidden_tokens
          - fn:
              params:
              - token
              body:
                std.logic.not:
                - std.string.contains:
                  - var: text
                  - var: token
        required: true
      - id: __export__policy.text.contains_pair
        assert:
          std.logic.and:
          - std.string.contains:
            - var: text
            - var: token_a
          - std.string.contains:
            - var: text
            - var: token_b
        required: true
```

## LIB-POLICY-TEXT-900

```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: read.text
      config: {}
    use:
    - ref: '#LIB-POLICY-TEXT-001'
      as: lib_policy_text
      symbols:
      - policy.text.contains_all
      - policy.text.contains_none
      - policy.text.contains_pair
contracts:
  clauses:
  - id: LIB-POLICY-TEXT-900
    title: text policy library smoke
    asserts:
      imports:
      - from: artifact
        names:
        - text
      checks:
      - id: assert_1
        assert:
        - call:
          - var: policy.text.contains_all
          - alpha beta gamma
          - lit:
            - alpha
            - beta
        - call:
          - var: policy.text.contains_pair
          - alpha beta gamma
          - alpha
          - gamma
        - call:
          - var: policy.text.contains_none
          - alpha beta gamma
          - lit:
            - delta
            - epsilon
        - std.logic.not:
          - call:
            - var: policy.text.contains_all
            - alpha beta gamma
            - lit:
              - alpha
              - delta
        - std.logic.not:
          - call:
            - var: policy.text.contains_none
            - alpha beta gamma
            - lit:
              - delta
              - beta
        required: true
```
