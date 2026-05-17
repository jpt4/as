# Self-Mailbox Unsupported Evidence Bundle

ADR-0073 adds `evidence/self_mailbox_unsupported_bundle.json`, the fifth AS
transition evidence bundle.

The bundle covers the positive
`UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` example named
`write buffer one unsupported preserved`, where a stem-right cell with
`self_mailbox` set to `write-buf-one` reports `self-mailbox-unsupported` and
preserves the cell unchanged.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_mailbox_unsupported_trace.json`;
- `schematics/self_mailbox_unsupported_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/stem_command_execution_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The evidence bundle validator checks that the preservation claim example
evaluates true, the proof certificate is accepted, the schematic trace
executes and matches the exact claim example, the committed SVG matches
renderer output, and the source-status boundary files remain present and
parseable.

## Boundary

The bundle records unsupported self-mailbox preservation only. It does not add
write-buffer command-token execution, `standard-signal` command-token
execution, recipient non-init command execution, priority, or sequencing.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted status rejection.
