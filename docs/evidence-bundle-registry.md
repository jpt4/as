# Evidence Bundle Registry

ADR-0066 adds `evidence/manifest.json`, the project registry for transition
evidence bundles.

The registry currently lists
`evidence/recipient_init_command_message_bundle.json`, the ADR-0065 bundle for
the positive fixed-upstream recipient init command-message transition. Future
bundle-producing ADRs should add one entry per bundle.

## Validation

`autarkic_systems/evidence_bundle.py` provides
`load_evidence_bundle_registry` and `validate_evidence_bundle_registry`.

The registry validator checks:

- registry schema and metadata;
- duplicate bundle IDs and paths;
- missing bundle files;
- agreement between each registry entry and the loaded bundle; and
- the full cross-layer validation for every registered bundle.

## Boundary

The registry is an index and batch-verification surface. It does not create new
Universal Cell behavior, new claims, or new source authority.

## Verification

Run:

```sh
python -m unittest tests.test_evidence_bundle_registry
```

The tests cover registry loading, the current ADR-0065 bundle entry, whole
registry validation, duplicate bundle-ID rejection, and missing bundle-path
rejection.
