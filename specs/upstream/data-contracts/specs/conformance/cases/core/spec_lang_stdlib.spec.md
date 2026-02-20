# Conformance Cases

## DCCONF-STDLIB-001

```yaml contract-spec
id: DCCONF-STDLIB-001
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: core numeric and set operators evaluate deterministically
purpose: Validates representative numeric operators in the stdlib profile.
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
    - std.logic.eq:
      - std.math.add:
        - 2
        - 3
      - 5
    - std.logic.eq:
      - std.math.sub:
        - 9
        - 4
      - 5
    - std.logic.eq:
      - std.math.add:
        - 1
        - 1
      - 2
    - std.logic.eq:
      - std.math.sub:
        - 3
        - 3
      - 0
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-002

```yaml contract-spec
id: DCCONF-STDLIB-002
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: core collection and object operators evaluate deterministically
purpose: Validates representative object and json operators in the stdlib profile.
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
    - std.logic.eq:
      - std.type.json_type:
        - std.json.parse:
          - '{"a":1,"b":2}'
        - dict
      - true
    - std.logic.eq:
      - std.object.has_key:
        - std.json.parse:
          - '{"a":{"b":1}}'
        - a
      - true
    - std.logic.eq:
      - std.type.json_type:
        - std.object.get:
          - std.json.parse:
            - '{"a":{"b":1}}'
          - a
        - dict
      - true
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-SCHEMA-STDLIB-003

```yaml contract-spec
id: DCCONF-STDLIB-003
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path operators evaluate deterministically
purpose: Validates pure contract-posix path helpers under ops.fs.path.
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
    - std.logic.eq:
      - ops.fs.path.normalize:
        - /a//b/./c
      - /a/b/c
    - std.logic.eq:
      - ops.fs.path.normalize:
        - /a/b/../c
      - /a/c
    - std.logic.eq:
      - ops.fs.path.join:
        - /a/b
        - c
      - /a/b/c
    - std.logic.eq:
      - ops.fs.path.extname:
        - file.tar.gz
      - .gz
    - std.logic.eq:
      - ops.fs.path.stem:
        - file.tar.gz
      - file.tar
    - std.logic.eq:
      - ops.fs.path.change_ext:
        - a/b.txt
        - md
      - a/b.md
    - std.logic.eq:
      - ops.fs.path.change_ext:
        - a/b.txt
        - ''
      - a/b
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-SCHEMA-STDLIB-004

```yaml contract-spec
id: DCCONF-STDLIB-004
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs file metadata helpers evaluate deterministically
purpose: Validates metadata-only file predicates and getters under ops.fs.file.
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
    - std.logic.eq:
      - ops.fs.file.exists:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
            exists: true
            type: file
            size_bytes: 12
      - true
    - std.logic.eq:
      - ops.fs.file.is_file:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
            exists: true
            type: file
      - true
    - std.logic.eq:
      - ops.fs.file.is_dir:
        - lit:
            path: /docs
            exists: true
            type: dir
      - true
    - std.logic.eq:
      - ops.fs.file.name:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
      - spec_lang_stdlib.spec.md
    - std.logic.eq:
      - ops.fs.file.parent:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
      - /specs/conformance/cases/core
    - std.logic.eq:
      - ops.fs.file.ext:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
      - .md
    - std.logic.eq:
      - ops.fs.file.get:
        - lit:
            path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
            exists: true
        - missing
        - fallback
      - fallback
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-005

```yaml contract-spec
id: DCCONF-STDLIB-005
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs json helpers evaluate deterministically
purpose: Validates pure json parse/path helpers under ops.fs.json.
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
    - std.logic.eq:
      - ops.fs.json.parse:
        - '{"a":{"b":[1,2,3]}}'
      - lit:
          a:
            b:
            - 1
            - 2
            - 3
    - std.logic.eq:
      - ops.fs.json.get:
        - lit:
            a:
              b:
              - 1
              - 2
              - 3
        - lit:
          - a
          - b
          - 1
      - 2
    - std.logic.eq:
      - ops.fs.json.get_or:
        - lit:
            a:
              b:
              - 1
              - 2
              - 3
        - lit:
          - a
          - c
        - fallback
      - fallback
    - std.logic.eq:
      - ops.fs.json.has_path:
        - lit:
            a:
              b:
              - 1
              - 2
              - 3
        - lit:
          - a
          - b
          - 0
      - true
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-006

```yaml contract-spec
id: DCCONF-STDLIB-006
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs json helpers fail schema for bad argument shapes
purpose: Ensures ops.fs.json path utilities reject invalid path shapes.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      std.logic.eq:
      - ops.fs.json.get:
        - lit:
            a: 1
        - a
      - 1
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-007

```yaml contract-spec
id: DCCONF-STDLIB-007
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs glob helpers evaluate deterministically
purpose: Validates pure glob matching/filter helpers under ops.fs.glob.
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
    - std.logic.eq:
      - ops.fs.glob.match:
        - specs/current.md
        - specs/*.md
      - true
    - std.logic.eq:
      - ops.fs.glob.filter:
        - lit:
          - specs/current.md
          - docs/book/index.md
          - README.md
        - specs/*.md
      - lit:
        - specs/current.md
    - std.logic.eq:
      - ops.fs.glob.any:
        - lit:
          - specs/current.md
          - docs/book/index.md
        - specs/*.md
      - true
    - std.logic.eq:
      - ops.fs.glob.all:
        - lit:
          - specs/current.md
        - specs/*.md
      - true
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-008

```yaml contract-spec
id: DCCONF-STDLIB-008
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs glob helpers fail schema for bad argument shapes
purpose: Ensures ops.fs.glob helpers reject invalid list element types.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      std.logic.eq:
      - ops.fs.glob.any:
        - lit:
          - 7
          - specs/current.md
        - specs/*.md
      - true
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-009

```yaml contract-spec
id: DCCONF-STDLIB-009
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path relativize and common_prefix evaluate deterministically
purpose: Validates pure relative-path and common-prefix helpers.
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
    - std.logic.eq:
      - ops.fs.path.relativize:
        - /a/b/c
        - /a/d/e
      - ../../d/e
    - std.logic.eq:
      - ops.fs.path.relativize:
        - a/b
        - a/b/c/d
      - c/d
    - std.logic.eq:
      - ops.fs.path.common_prefix:
        - lit:
          - /a/b/c.md
          - /a/b/d.md
      - /a/b
    - std.logic.eq:
      - ops.fs.path.common_prefix:
        - lit:
          - specs/current.md
          - specs/schema/schema_v1.md
      - specs
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-010

```yaml contract-spec
id: DCCONF-STDLIB-010
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path common_prefix fails schema for non-string entries
purpose: Ensures common_prefix rejects list entries that are not strings.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      std.logic.eq:
      - ops.fs.path.common_prefix:
        - lit:
          - /a/b
          - 7
      - /a
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-011

```yaml contract-spec
id: DCCONF-STDLIB-011
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path parents and within evaluate deterministically
purpose: Validates pure parent chain and containment helpers.
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
    - std.logic.eq:
      - ops.fs.path.parents:
        - /a/b/c
      - lit:
        - /a/b
        - /a
        - /
    - std.logic.eq:
      - ops.fs.path.parents:
        - a/b/c
      - lit:
        - a/b
        - a
        - .
    - std.logic.eq:
      - ops.fs.path.within:
        - /a/b
        - /a/b/c/d
      - true
    - std.logic.eq:
      - ops.fs.path.within:
        - specs
        - specs/current.md
      - true
    - std.logic.eq:
      - ops.fs.path.within:
        - /a/b
        - /a/c
      - false
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-012

```yaml contract-spec
id: DCCONF-STDLIB-012
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path parents fails schema for non-string argument
purpose: Ensures parents rejects non-string input.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      std.logic.eq:
      - ops.fs.path.parents:
        - 7
      - lit: []
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-013

```yaml contract-spec
id: DCCONF-STDLIB-013
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path compare and sort evaluate deterministically
purpose: Validates pure normalized path compare and sort helpers.
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
    - std.logic.eq:
      - ops.fs.path.compare:
        - /a//b
        - /a/b
      - 0
    - std.logic.eq:
      - ops.fs.path.compare:
        - /a/b
        - /a/c
      - -1
    - std.logic.eq:
      - ops.fs.path.sort:
        - lit:
          - /b/z
          - /a//c
          - /a/b
      - lit:
        - /a/b
        - /a/c
        - /b/z
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```

## DCCONF-STDLIB-014

```yaml contract-spec
id: DCCONF-STDLIB-014
spec_version: 1
schema_ref: /specs/schema/schema_v1.md
title: ops fs path sort fails schema for non-string entries
purpose: Ensures sort rejects list entries that are not strings.
type: contract.check
expect:
  portable:
    status: fail
    category: schema
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
      std.logic.eq:
      - ops.fs.path.sort:
        - lit:
          - /a/b
          - 7
      - lit:
        - /a/b
harness:
  check:
    profile: text.file
    config:
      path: /specs/conformance/cases/core/spec_lang_stdlib.spec.md
```
