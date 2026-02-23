# Bundle Bootstrap Governance Contract (v1)

## Purpose

Define one-time bootstrap behavior for self-governed tooling bundles.

## Rules

- bootstrap lock must contain exactly one bundle entry
- bootstrap bundle id must equal `data-contracts-bundler`
- package checksum verification is mandatory
- unpacked payload must include `resolved_bundle_lock_v1.yaml` and `resolved_files.sha256`
- repeated bootstrap must fail unless explicit force mode is selected
- after bootstrap, normal install/check workflows use root `bundles.lock.yaml`
