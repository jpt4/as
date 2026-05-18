# ADR-0169: Recipient Write-Buffer Command Execution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0168 resolves delivered recipient `write-buf-zero` and `write-buf-one`
command-message semantics as source-ready append behavior. The runtime still
rejects those command messages under the older recipient non-init boundary, so
project status truthfully reports a source-ready but not-yet-implemented
surface.

The next executable slice is to replace that checked recipient write-buffer
rejection boundary with append execution while keeping the remaining
standard-signal command-token rejection boundary intact. Multiple simultaneous
recipient command-message inputs remain a reject-and-clear conflict policy.

This also affects composed neighbor delivery. A neighbor-delivered
write-buffer command is no longer a recipient rejection chain once recipient
write-buffer execution exists; it becomes a consumed neighbor-delivery chain
through recipient write-buffer append behavior. The rejection chain should
remain available for delivered `standard-signal` command tokens.

## Decision

Implement recipient-side write-buffer command-message execution for
`write-buf-zero` and `write-buf-one`.

A recipient write-buffer command message appends the command's literal bit to
the recipient cell buffer, clears the active command-message input source,
preserves role, memory, output, automail, self-mailbox, and control, and
returns `recipient-write-buffer-command-message-appended`. The existing
full-buffer boundary is preserved: a full buffer reports `stem-buffer-full`
without changing the cell.

Single delivered `standard-signal` command messages remain rejected.
Conflicting command-message inputs still reject and clear the active command
input rather than selecting a priority.

## Success Criteria

- Red tests fail before implementation because recipient write-buffer command
  messages still report `rejected-input`, the new status/predicate/claim are
  absent, and project status still lists write-buffer as blocked.
- Direct and upstream recipient write-buffer command-message inputs append
  literal bits and clear their active command source.
- Existing recipient non-init rejection claims no longer cover single
  write-buffer command messages, but still cover standard-signal and
  multi-command conflicts.
- A new transition claim/proof surface covers recipient write-buffer append
  execution.
- Neighbor delivery treats delivered write-buffer commands as consumed by
  recipient write-buffer behavior, while delivered `standard-signal` remains a
  rejection-chain witness.
- Project/source status report only `standard-signal` as blocked and move
  write-buffer safe-next guidance to evidence-bundle promotion.
- Runtime behavior changes only for single recipient `write-buf-zero` and
  `write-buf-one` command-message inputs.

## Test Plan

- Red: add focused runtime, claim/proof/language, chain, and status tests,
  then run them before implementation.
- Green: implement runtime behavior, predicate/object-language/claim/proof
  updates, chain expectation updates, and source/project status updates.
- Regression: run focused suites, project/source status JSON, claim/proof and
  chain validators, JSON parsing, `compileall`, `git diff --check`, and full
  unittest discovery.

## After Action Report

Implemented on 2026-05-18.

The red phase added focused runtime, claim/proof/language, chain, and
source-status tests before implementation. The focused red run executed 151
tests and failed for the expected reasons: recipient write-buffer command
messages still returned `rejected-input`, the new status and predicate were
absent, source/project status still listed write-buffer as blocked, and the
chain/evidence manifests still encoded the old rejection boundary.

The implementation added recipient-side command-message append execution in
the universal-cell transition path, introduced the
`recipient-write-buffer-command-message-appended` status, added the matching
transition predicate, claim, proof certificate, and object-language entries,
and moved single write-buffer command messages out of the recipient non-init
rejection claim. Neighbor-delivery chain surfaces now treat delivered
write-buffer commands as consumed append behavior while preserving delivered
`standard-signal` as the rejection-chain witness. Source-status and
project-status reports now aggregate only `standard-signal` as the remaining
blocked command.

Verification passed after implementation: the focused ADR-0169 suite ran 230
tests, project-status JSON accepted schema 15 with 16 transition claims and 40
examples, source-status JSON accepted schema 2, the transition evidence
registry accepted 10 bundles, the chain evidence registry accepted 2 bundles,
all JSON files parsed, `compileall` passed, `git diff --check` passed, and
full unittest discovery ran 744 tests successfully.
