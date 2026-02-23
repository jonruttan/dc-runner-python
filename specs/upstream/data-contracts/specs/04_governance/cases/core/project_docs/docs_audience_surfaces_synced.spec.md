```yaml contract-spec
id: DCGOV-DOCS-AUD-002
title: docs audience surfaces synced
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
contracts:
  clauses:
    - id: docs_audience_sync
      asserts:
        checks:
          - id: assert_1
            assert:
              std.string.contains:
                - "audience"
                - "audience"
```
