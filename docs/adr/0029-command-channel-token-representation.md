# ADR-0029: Command Channel Token Representation

Date: 2026-05-17

Status: Accepted

## Context

ADR-0027 identified command-message output representation as the next blocker
after self mailbox state. ADR-0028 added the self mailbox field, but AS channel
tuples still only accept binary values, `_`, and the older `si` shorthand. The
PRC process-buffer sketch routes neighbor-target command messages onto output
channels, so AS needs a representation for those tokens before it can implement
delivery.

This ADR adds channel-token representation only. It does not route command
buffers, execute mailbox messages, or reinterpret existing `si` behavior.

## Decision

Allow Universal Cell channel tuples to carry the eight ADR-0026 command IDs as
tokens:

- the existing binary values, `_`, and `si` remain valid;
- `standard-signal`, `stem-init`, `wire-r-init`, `wire-l-init`, `proc-r-init`,
  `proc-l-init`, `write-buf-zero`, and `write-buf-one` become valid channel
  tokens;
- the transition-claim object-language `signals` term list must expose the
  expanded channel-token vocabulary;
- current transition functions may preserve or reject command-message inputs,
  but must not execute them as command-buffer semantics.

## Success Criteria

- Red tests fail before implementation because command-message output tokens
  are invalid channel values and the object language does not list them as
  signals.
- Command-message output tokens can be represented and preserved by blocked
  output.
- Command-message inputs are accepted as state but still rejected by the current
  stem transition instead of executing.
- Unknown channel tokens remain rejected.
- The object language validates the expanded signal vocabulary.

## Consequences

- Neighbor-target command delivery now has a representable output token shape
  for a later ADR.
- This broadens channel state without broadening execution semantics.
- The `si` shorthand remains the only currently executed fixed-cell stem-init
  input.

## After Action Report

Red step:

- `python -m unittest tests.test_command_channel_tokens` failed because
  command-message channel values were invalid and the object-language
  `signals` vocabulary did not include them.

Green step:

- Expanded `Signal` and channel validation in
  `autarkic_systems/universal_cell.py`.
- Updated `language/transition_claim_language.json`.
- `python -m unittest tests.test_command_channel_tokens` passed 6 tests.

Full verification:

- `python -m unittest discover` passed 149 tests.
- `python -m py_compile autarkic_systems/universal_cell.py
  autarkic_systems/object_language.py tests/test_command_channel_tokens.py`
  passed.
- `jq -e . language/transition_claim_language.json` passed.
- `git diff --check` passed.

Coverage limits:

- This is representation only.
- It does not route command buffers.
- It does not deliver command-message outputs to neighbors.
- It does not execute command-message inputs.
