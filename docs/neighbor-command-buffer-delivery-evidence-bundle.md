# Neighbor Command-Buffer Delivery Evidence Bundle

ADR-0076 adds `evidence/neighbor_command_buffer_delivery_bundle.json`, the
eighth AS transition evidence bundle.

The bundle covers the positive
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` example named
`neighbor b proc left command delivered`, where a matching standard input
completes buffer `10101`, decodes it as `neighbor-b/proc-l-init`, clears the
consumed command state, and places `proc-l-init` on output channel 1.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/neighbor_command_buffer_delivery_trace.json`;
- `schematics/neighbor_command_buffer_delivery_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/stem_command_execution_source_status.json`;
- `sources/recipient_command_consumption_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The evidence bundle validator checks that the delivery claim example evaluates
true, the proof certificate is accepted, the schematic trace executes and
matches the exact claim example, the committed SVG matches renderer output, and
the source-status boundary files remain present and parseable.

## Boundary

The bundle records neighbor-target decoded-command delivery only. It does not
execute the delivered token on a recipient cell, add recipient non-init command
execution, add `standard-signal` command-token execution, add write-buffer
command-token execution, or define priority and sequencing.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_command_buffer_delivery_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted status rejection.
