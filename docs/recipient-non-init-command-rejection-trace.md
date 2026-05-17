# Recipient Non-Init Command Rejection Trace

Status: implemented by ADR-0055 on 2026-05-17.

The structured trace lives in
`schematics/recipient_non_init_command_rejection_trace.json`.

## Boundary

This artifact records one recipient-side non-init command-message rejection.
The before cell is a fixed processor with left memory and an upstream
`standard-signal` token on channel 1. The current AS transition pulls that
token, rejects it with status `rejected-input`, preserves role and memory,
clears upstream/input/output channels, and leaves automail, self-mailbox,
control, and buffer state unchanged.

This trace deliberately does not execute `standard-signal`,
`write-buf-zero`, `write-buf-one`, or multiple simultaneous command-message
tokens. ADR-0053 records why those semantics remain blocked, and ADR-0054
names the rejection predicate that this trace satisfies.

## Validation

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_rejection_trace
```

The tests check artifact identity, schema vocabulary, upstream command flow,
execution replay, the ADR-0054 transition predicate, PRC witness validation,
and drift rejection for role changes, uncleared upstream state, and mismatched
flow text.
