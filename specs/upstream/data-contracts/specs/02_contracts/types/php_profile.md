# PHP Subject Profile Contract (v1)

PHP-specific values MUST be projected to JSON subject envelopes.

Projection rules:

- associative array -> JSON object in `value` with `meta.php_array_kind: "assoc"`
- sequential array -> JSON array in `value` with `meta.php_array_kind: "list"`
- unsupported runtime objects -> deterministic adapter failure.

Profile id: `php.generic/v1`.
