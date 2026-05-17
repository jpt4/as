# Multi-Command Rejection Evidence Bundle

ADR-0069 adds `evidence/multi_command_recipient_rejection_bundle.json`, the
third AS transition evidence bundle.

The bundle covers the positive
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` example named
`fixed all-init command conflict rejected`, where a wire-right recipient sees
simultaneous `wire-r-init` and `proc-l-init` command-message tokens, rejects
the activation, preserves role and memory, and clears active input.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/multi_command_recipient_rejection_trace.json`;
- `schematics/multi_command_recipient_rejection_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/multi_command_recipient_input_policy_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The existing evidence bundle validator checks that the conflict rejection
claim example evaluates true, the proof certificate is accepted, the schematic
trace executes and validates against the PRC hardware witness map, the
committed SVG matches renderer output, and the source-status boundary files
remain present and parseable.

## Boundary

The bundle records a simultaneous-command rejection boundary. It does not add
priority, sequencing, non-init command execution, `standard-signal`
command-token execution, or write-buffer command-token execution.

## Verification

Run:

```sh
python -m unittest tests.test_multi_command_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted claim-ID rejection.
