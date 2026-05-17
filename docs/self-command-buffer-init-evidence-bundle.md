# Self Command-Buffer Init Evidence Bundle

ADR-0074 adds `evidence/self_command_buffer_init_bundle.json`, the sixth AS
transition evidence bundle.

The bundle covers the positive `UC-STEM-COMMAND-BUFFER-SELF-INIT` example
named `self command buffer processor left init`, where a matching standard
input completes buffer `00101`, decodes it as `self/proc-l-init`, and
reconfigures the stem cell into processor-left while clearing transient command
state.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_command_buffer_init_trace.json`;
- `schematics/self_command_buffer_init_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/stem_command_execution_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The evidence bundle validator checks that the dispatch claim example evaluates
true, the proof certificate is accepted, the schematic trace executes and
matches the exact claim example, the committed SVG matches renderer output,
and the source-status boundary files remain present and parseable.

## Boundary

The bundle records self-target init-family command-buffer dispatch only. It
does not add self-target non-init command execution, recipient non-init command
execution, `standard-signal` command-token execution, or write-buffer
command-token execution.

## Verification

Run:

```sh
python -m unittest tests.test_self_command_buffer_init_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted claim-ID rejection.
