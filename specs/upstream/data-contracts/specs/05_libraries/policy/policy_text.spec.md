```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
    check:
      profile: text.file
      config: {}
    use:
    - ref: '#LIB-POLICY-TEXT-001'
      as: lib_policy_text
      symbols:
      - policy.text.contains_all
      - policy.text.contains_none
      - policy.text.contains_pair
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
      owner: data-contracts
      tags:
      - policy
      - text
    type: contract.export
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
      - id: __export__policy.text.contains_pair
        assert:
          std.logic.and:
          - std.string.contains:
            - var: text
            - var: token_a
          - std.string.contains:
            - var: text
            - var: token_b
  - id: LIB-POLICY-TEXT-900
    title: text policy library smoke
    type: contract.check
    asserts:
      imports:
      - from: asset
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
adapters:
- type: beta.exports_as_policy_text_contains_all_from_assert_function_path_export_policy_text_contains_all_params_text_required_tokens_required_true_as_policy_text_contains_none_from_assert_function_path_export_policy_text_contains_none_params_text_forbidden_tokens_required_true_as_policy_text_contains_pair_from_assert_function_path_export_policy_text_contains_pair_params_text_token_a_token_b_required_true
  actions:
  - id: act.lib.policy.text.spec.1
    profile: default
- type: beta.check_profile_text_file_config_use_ref_lib_policy_text_001_as_lib_policy_text_symbols_policy_text_contains_all_policy_text_contains_none_policy_text_contains_pair
  actions:
  - id: act.lib.policy.text.spec.2
    profile: default
services:
- id: svc.lib.policy.text.spec.1
  consumes:
  - act.lib.policy.text.spec.1
- id: svc.lib.policy.text.spec.2
  consumes:
  - act.lib.policy.text.spec.2
```


