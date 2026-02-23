```yaml contract-spec
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
harness:
  type: unit.test
  profile: check
  config:
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
contracts:
  clauses:
  - id: DCGOV-DOCS-REF-026
    title: readme avoids makefile onboarding cookbook
    purpose: Keeps README focused on project purpose and usage, not local make workflows.
    asserts:
      imports:
      - from: asset
        names:
        - violation_count
      checks:
      - id: assert_1
        assert:
          call:
          - var: policy.assert.no_violations
          - std.object.assoc:
            - violation_count
            - var: violation_count
            - lit: {}
adapters:
- type: beta.scan
  actions:
  - id: act.gov.docs.readme.makefile.coo.1
    direction: bidirectional
    profile: default
services:
- id: svc.gov.docs.readme.makefile.coo.1
  consumes:
  - act.gov.docs.readme.makefile.coo.1
```
