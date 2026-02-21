```yaml contract-spec
id: DCGOV-DOCS-REF-026
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: readme avoids makefile onboarding cookbook
purpose: Keeps README focused on project purpose and usage, not local make workflows.
type: contract.check
harness:
  root: .
  readme_makefile_tokens:
    path: /README.md
    forbidden_tokens:
    - make setup
    - make prepush
    - hooks-install
  check:
    profile: governance.scan
    config:
      check: docs.readme_makefile_cookbook_forbidden
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - violation_count
  steps:
  - id: assert_1
    assert:
      std.logic.eq:
      - {var: violation_count}
      - 0
```
