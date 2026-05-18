# Self-Mailbox Write-Buffer Evidence Bundle

ADR-0162 adds `evidence/self_mailbox_write_buffer_bundle.json` and registers
it in `evidence/manifest.json`.

The bundle ties the direct `write-buf-one` self-mailbox execution path to:

- `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED`;
- positive example `self mailbox write buffer one appended`;
- covered positive examples for both `write-buf-zero` and `write-buf-one`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_mailbox_write_buffer_trace.json`;
- `schematics/self_mailbox_write_buffer_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the stem, recipient non-init, standard-signal, and write-buffer source-status
  files.

This bundle adds no runtime behavior. It makes the already implemented
ADR-0161 direct self-mailbox write-buffer behavior inspectable across runtime,
claim, proof, trace, render, hardware-witness, and source-status layers.

Recipient write-buffer command-message input remains rejected by the recipient
non-init boundary, and `standard-signal` command-token execution remains
source-blocked.
