# ADR-0162: Write-Buffer Execution Evidence Bundles

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0161 implemented the source-resolved write-buffer command execution
surfaces:

- direct stem `self_mailbox` commands `write-buf-zero` and `write-buf-one`;
- completed self-target command buffers decoding to `write-buf-zero` and
  `write-buf-one`.

Those behaviors now have runtime tests, transition claims, proof certificates,
and object-language coverage. They are still missing the integrated evidence
bundle layer that ties one runtime example to its claim, proof certificate,
schematic trace, rendered SVG, hardware witness map, and source-status
boundaries.

## Decision

Add two transition evidence bundles:

- `evidence/self_mailbox_write_buffer_bundle.json`, covering direct
  self-mailbox `write-buf-one` execution under
  `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED`; and
- `evidence/self_command_buffer_write_buffer_bundle.json`, covering completed
  self-target command-buffer `write-buf-one` execution under
  `UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED`.

Each bundle will use the `write-buf-one` positive example as its primary
trace-aligned example and will list both the zero and one positive claim
examples as covered evidence.

This ADR does not add new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the new trace IDs, trace
  artifacts, SVG artifacts, and bundle files are absent.
- The direct self-mailbox trace validates that `write-buf-one` appends literal
  `1`, clears `self_mailbox`, preserves role, memory, upstream, output, and
  control, and records status `self-mailbox-write-buffer-appended`.
- The completed self-target command-buffer trace validates that buffer
  `0011` plus matching input decodes value `7` as `self/write-buf-one`, clears
  the command source, preserves the control rail, resets the buffer to the
  literal append bit, and records status
  `stem-command-buffer-self-write-buffer-appended`.
- The committed SVGs exactly match renderer output.
- The evidence registry contains ten transition bundles and validates all ten.
- The write-buffer source-status frontier no longer points at the now-complete
  evidence-bundle task.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers both implemented write-buffer self-target
surfaces. Recipient write-buffer command-message input remains under the
recipient non-init rejection boundary, and `standard-signal` command-token
execution remains source-blocked.

## Test Plan

- Red:
  `python -m unittest tests.test_self_mailbox_write_buffer_trace tests.test_self_mailbox_write_buffer_svg tests.test_self_command_buffer_write_buffer_trace tests.test_self_command_buffer_write_buffer_svg tests.test_write_buffer_execution_evidence_bundle`
  fails before the new trace, SVG, and bundle artifacts are added.
- Green: the same focused suite passes after adding the artifacts and
  validator support.
- Regression: run the evidence registry and CLI tests, source/project status
  tests, focused write-buffer tests, JSON parsing, `compileall`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The focused red run failed before implementation because the new schematic
trace IDs, SVG artifact constants, bundle files, registry entries, and updated
write-buffer safe-next slice were absent.

The implementation adds trace validation and SVG rendering support for direct
self-mailbox write-buffer append and completed self-target command-buffer
write-buffer append. It adds two trace JSON artifacts, two renderer-generated
SVGs, two transition evidence bundles, and registry entries for both bundles.

The write-buffer source-status record now points its safe next slice at
recipient write-buffer command-message source resolution, because the
self-target execution evidence task is complete.

Verification passed:

- focused red suite failed before implementation as expected;
- focused green suite passed 178 tests;
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`
  accepted 10 transition evidence bundles;
- evidence registry JSON, project-status JSON, and source-status JSON commands
  accepted the current artifacts;
- JSON parsing passed for the new and touched JSON artifacts;
- `python -m compileall -q autarkic_systems tests` passed;
- `git diff --check` passed; and
- `python -m unittest discover` ran 728 tests.
