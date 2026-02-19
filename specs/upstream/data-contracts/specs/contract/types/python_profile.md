# Python Subject Profile Contract (v1)

Python-specific native values MUST be projected to JSON subject envelopes.

Projection rules:

- native tuple -> JSON array in `value`, with `meta.native_kind: "python.tuple"`
- native dict -> JSON object in `value`
- unsupported native objects -> deterministic schema/runtime error in adapter,
  never evaluator-native subject values.

Profile id: `python.generic/v1`.
