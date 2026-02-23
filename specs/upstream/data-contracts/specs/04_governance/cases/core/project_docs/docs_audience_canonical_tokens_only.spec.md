```yaml contract-spec
id: DCGOV-DOCS-AUD-003
title: docs audience canonical tokens only
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
contracts:
  clauses:
    - id: docs_audience_tokens
      asserts:
        checks:
          - id: assert_1
            assert:
              std.string.contains:
                - "implementer"
                - "implementer"
```
