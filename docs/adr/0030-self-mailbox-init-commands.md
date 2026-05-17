# ADR-0030: Self Mailbox Init Commands

Date: 2026-05-17

Status: Accepted

## Context

ADR-0028 added `Cell.self_mailbox`; ADR-0029 made command-message channel
tokens representable. The PRC formal model then gives a narrow next execution
step: when the self mailbox contains a special message and input/output are
clear, `process-special-message` can act on the current cell.

Full command execution remains too broad. The source table still leaves
`standard-signal` command behavior unresolved, and legacy sketches disagree on
whether `write-buf-zero` / `write-buf-one` append and retain buffer state or are
cleared by a later reset. The stable slice is therefore only the init family:
`stem-init`, `wire-r-init`, `wire-l-init`, `proc-r-init`, and `proc-l-init`.

## Decision

Teach `step_stem_cell` to process self-mailbox init commands when output is
empty, automail is empty, and input is empty:

- `stem-init` resets the cell to canonical stem state;
- `wire-r-init`, `wire-l-init`, `proc-r-init`, and `proc-l-init` reconfigure the
  cell to the named fixed role and memory;
- successful self-mailbox processing clears input, output, automail,
  `self_mailbox`, control, and buffer;
- `standard-signal`, `write-buf-zero`, and `write-buf-one` remain explicit
  unsupported self-mailbox commands for now.

This ADR does not decode a full command buffer, route neighbor messages, or
execute command-message input tokens.

## Success Criteria

- Red tests fail before implementation because self-mailbox commands are idle
  and the status vocabulary lacks the new outcomes.
- Init-family mailbox commands produce the expected role/memory reset and clear
  the self mailbox.
- Unsupported mailbox commands are reported without mutation.
- Occupied output still blocks mailbox processing.
- Existing automail priority remains intact.
- The transition-claim object language exposes the new statuses.

## Consequences

- AS now has the first source-backed self-mailbox execution slice.
- Write-buffer and `standard-signal` command semantics remain deliberate future
  work.
- This is still not full stem command-buffer execution.

## After Action Report

Red step:

- `python -m unittest tests.test_self_mailbox_init_commands` failed because
  self-mailbox commands returned `idle` and the transition-language status
  vocabulary lacked `self-mailbox-processed` and `self-mailbox-unsupported`.

Green step:

- Added self-mailbox init-command processing to
  `autarkic_systems/universal_cell.py`.
- Added explicit unsupported handling for `standard-signal`,
  `write-buf-zero`, and `write-buf-one`.
- Updated `language/transition_claim_language.json`.
- `python -m unittest tests.test_self_mailbox_init_commands` passed 7 tests.

Full verification:

- `python -m unittest discover` passed 156 tests.
- `python -m py_compile autarkic_systems/universal_cell.py
  tests/test_self_mailbox_init_commands.py` passed.
- `jq -e . language/transition_claim_language.json` passed.
- `git diff --check` passed.

Coverage limits:

- This does not decode a full command buffer.
- This does not deliver neighbor-target command messages.
- This does not execute `standard-signal`, `write-buf-zero`, or
  `write-buf-one` from the self mailbox.
