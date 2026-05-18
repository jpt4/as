# Post-Handoff Signal Witness

ADR-0196 adds `autarkic_systems.network_sequence`, a bounded follow-up witness
over the two-cell neighbor-delivery witness.

## Purpose

The two-cell witness shows that a neighbor-delivered init command can
reconfigure a recipient. The post-handoff signal witness checks the next
observable consequence: after delivery of `proc-l-init`, the recipient is a
`proc/left` cell, and a later binary input routes through the existing
fixed-cell transition while toggling processor memory.

## Run

```sh
python -m autarkic_systems.network_sequence
python -m autarkic_systems.network_sequence --format json
python -m autarkic_systems.network_sequence --case write-buffer-handoff-not-init
python -m autarkic_systems.network_sequence --case malformed-followup-rejected
```

The checked fixture cases are:

- `init-followup-routed`: delivered `proc-l-init` reconfigures the recipient to
  `proc/left`; a later binary `(1, 0, 0)` input routes to output `(0, 0, 1)`
  and toggles memory to `right`.
- `write-buffer-handoff-not-init`: a consumed write-buffer delivery is rejected
  for this witness because it is not an init-family reconfiguration handoff.
- `malformed-followup-rejected`: an accepted init delivery is preserved in the
  payload, but a non-binary follow-up input is rejected by the existing
  fixed-cell transition.

## Boundary

This is not a scheduler or simulator. It composes one accepted two-cell witness
with one explicit follow-up recipient step. It does not decide timing, topology,
output clearing, queued delivery, or new command semantics.
