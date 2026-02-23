# Regex Portability Profile (v1)

This document defines a portability profile for `regex` assertions used in
spec tests. The goal is cross-runtime determinism across implementations such
as Python and PHP.

Normative policy linkage:

- `ASSERT_HEALTH_NON_PORTABLE_REGEX_DIAGNOSTIC`
  (`specs/02_contracts/policy_v1.yaml`)

## Guidance

- Specs SHOULD use only portable regex constructs.
- Implementations SHOULD emit assertion-health diagnostics for non-portable
  constructs.

## Portable Baseline

The following constructs are intended to be portable across runtimes:

- literals and escaped literals
- character classes (`[a-z]`, `[^0-9]`)
- anchors (`^`, `$`, `\\A`, `\\Z`)
- alternation (`a|b`)
- grouping (`(...)`, `(?:...)`)
- quantifiers (`?`, `*`, `+`, `{m}`, `{m,n}`)

## Non-Portable Constructs (Diagnostic Candidates)

Implementations SHOULD diagnose patterns using:

- lookbehind (`(?<=...)`, `(?<!...)`)
- named capture groups (`(?P<name>...)`, `(?<name>...)`)
- named backreferences (`\\k<name>`)
- conditional groups (`(?(...)...)`)
- inline flags (`(?i)`, `(?m:...)`, etc.)
- atomic groups (`(?>...)`)
- possessive quantifiers (`*+`, `++`, `?+`)

## Notes

- This profile intentionally favors deterministic portability over maximal
  regex feature coverage.
- Runners may accept additional constructs, but those constructs are outside
  the portable profile and should be diagnosed under assertion-health policy.
