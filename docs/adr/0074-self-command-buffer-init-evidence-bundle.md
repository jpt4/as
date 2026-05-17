# ADR-0074: Self Command-Buffer Init Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0072 and ADR-0073 registered the direct self-mailbox execution and
preservation paths. The next self-target command surface is the completed
command-buffer init dispatch from ADR-0037 through ADR-0040.

That surface already has a runtime transition, named claim, proof certificate,
schematic trace, rendered SVG, and source-status boundary. It should enter the
evidence registry so the registry covers not only direct self-mailbox tokens,
but also a decoded self-target command buffer that dispatches to the same
init-family behavior.

## Decision

Add `evidence/self_command_buffer_init_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-STEM-COMMAND-BUFFER-SELF-INIT`;
- the positive manifest example `self command buffer processor left init`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_command_buffer_init_trace.json`;
- `schematics/self_command_buffer_init_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep self-target init-family execution,
  non-init, `standard-signal`, and write-buffer boundaries explicit.

This ADR does not add Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the self command-buffer bundle
  is absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes, validates against the PRC
  hardware witness map, and exactly matches the named claim example.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains six bundles and the CLI validates all six.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers the decoded self-target init command-buffer
path alongside direct self-mailbox init execution. The command-buffer dispatch
remains deliberately narrower than full command execution: self-target non-init
commands, `standard-signal` command-token execution, and write-buffer
command-token execution stay source-blocked.

## Test Plan

- Red: `python -m unittest tests.test_self_command_buffer_init_evidence_bundle`
  fails before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle and registry
  entry.
- Regression: run evidence registry/CLI tests, adjacent self command-buffer
  tests, and the full default suite before commit.

## After Action Report

Implemented in `evidence/self_command_buffer_init_bundle.json` and registered
in `evidence/manifest.json`.

The focused red run failed because
`evidence/self_command_buffer_init_bundle.json` was absent. The green
implementation adds the bundle for the positive
`self command buffer processor left init` example under
`UC-STEM-COMMAND-BUFFER-SELF-INIT`.

Unlike the direct self-mailbox bundles, the self command-buffer trace already
matched the named claim example exactly, so this slice required no trace or SVG
fixture alignment. Bundle validation now proves one completed self-target
command-buffer init dispatch across claim, proof, trace, render, hardware
witness map, and source-status boundaries.

The evidence registry and CLI now validate six bundles: recipient init
execution, recipient single-token non-init rejection, recipient
simultaneous-token rejection, direct self-mailbox init execution, direct
self-mailbox unsupported preservation, and completed self-target
command-buffer init dispatch.

Runtime behavior remains unchanged. AS still does not execute self-target
non-init, recipient non-init, `standard-signal` command-token, or write-buffer
command-token semantics.
