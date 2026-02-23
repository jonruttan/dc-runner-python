```yaml contract-spec
id: DCCONF-PROFILE-001
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: subject profile schema defines canonical envelope fields
purpose: Ensures subject profile schema defines JSON-core envelope and deterministic projection
  constraints.
type: contract.check
expect:
  portable:
    status: pass
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
      - profile_id
    - std.string.contains:
      - {var: text}
      - profile_version
    - std.string.contains:
      - {var: text}
      - json_core_only
    - std.string.contains:
      - {var: text}
      - deterministic_projection
harness:
  check:
    profile: text.file
    config:
      path: /specs/01_schema/subject_profiles_v1.yaml
```


```yaml contract-spec
id: DCCONF-PROFILE-002
spec_version: 1
schema_ref: /specs/01_schema/schema_v1.md
title: text.file exposes context_json subject profile envelope
purpose: Ensures text.file harness provides context_json target with profile metadata and
  JSON value payload.
type: contract.check
expect:
  portable:
    status: pass
contract:
  defaults:
    class: MUST
  imports:
  - from: artifact
    names:
    - context_json
  steps:
  - id: assert_1
    assert:
    - std.logic.eq:
      - std.object.get:
        - {var: context_json}
        - profile_id
      - text.file/v1
    - std.logic.eq:
      - std.object.get:
        - {var: context_json}
        - profile_version
      - 1
    - std.object.has_key:
      - {var: context_json}
      - value
    - std.object.has_key:
      - {var: context_json}
      - meta
harness:
  check:
    profile: text.file
    config:
      path: /specs/02_contracts/20_subject_profiles_v1.md
```
