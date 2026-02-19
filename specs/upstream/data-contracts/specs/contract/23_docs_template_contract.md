# Docs Template Contract (v1)

`docs.generate` templates use a moustache-core subset.

Supported tags:

- `{{var}}`: variable interpolation (dotted lookup supported)
- `{{#section}}...{{/section}}`: list/truthy section
- `{{^section}}...{{/section}}`: inverted section

Rules:

- template evaluation is pure (no function execution inside templates)
- missing keys are schema errors in strict mode
- output writes are owned by harness mode:
  - `markers`: replace only generated marker blocks
  - `full_file`: replace full output file content
