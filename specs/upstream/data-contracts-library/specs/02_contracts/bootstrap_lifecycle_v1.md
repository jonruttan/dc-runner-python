# Bootstrap Lifecycle Contract (v1)

## Marker

Bootstrap success marker path:

- `.bundler/bootstrap.state.json`

Marker MUST include:

- `version` (integer, const 1)
- `bundle_id`
- `bundle_version`
- `source.asset_url`
- `source.sha256`
- `installed_at`

## Transition Rules

- first successful bootstrap writes marker
- subsequent bootstrap without force MUST fail
- forced bootstrap replaces installed bundle and updates marker
- after bootstrap, verification and governance consume installed bundle content from `.bundles/data-contracts-bundler`
