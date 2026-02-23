```yaml contract-spec
id: DCGOV-DOCS-AUD-001
title: docs audience surfaces generated
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
contracts:
  clauses:
    - id: docs_audience_surfaces
      asserts:
        checks:
          - id: assert_1
            assert:
              std.string.contains:
                - "docs/audience"
                - "docs/audience"
```
