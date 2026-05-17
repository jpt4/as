# ASMSIM Process-Buffer Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/asmsim_process_buffer_status.json`.

## Decision

Do not implement `standard-signal` or write-buffer command-token execution
from `practice/asmsim.scm`.

The witness is useful because it is a newer Universal Cell ASM simulator, but
the process-buffer section is not a settled command-semantics source:

- the `qs18` process-buffer block says it needs documentation;
- the process-buffer auxiliary block says `XXX CONFIRM MSGLIST CODES`;
- the command branches are predicate families such as `id+msg?`,
  `id+10b5?`, `id+11b5?`, `tar+0b4?`, `tar+sic?`, `id+nop?`, and
  `tar+nop?`;
- the message-code layer contains a literal `msg-list` placeholder;
- the source does not name `standard-signal`, `write-buf-zero`, or
  `write-buf-one` command tokens.

## AS Boundary

This witness strengthens the blocker recorded by ADR-0057, ADR-0058, and
ADR-0062. AS should keep command-token execution blocked until a later ADR
reconciles the formal named command table, the legacy simulator divergences,
and ASMSIM's incomplete process-buffer message-code documentation.

## Verification

Run:

```sh
python -m unittest tests.test_asmsim_process_buffer_status
```

The tests check the source-only decision, the warning comments, the
process-buffer branch families, the message-code placeholder, and the
cross-links from the existing command source-status artifacts.
