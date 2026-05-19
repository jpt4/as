# Proflog frontier status

Status: 2026-05-19 — Proflog blockers **resolved** via authoritative pin.

## Authoritative repository

[autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) at
`14d3150ed3a8029347b8981d657a22a1efde2753` implements the SJAS ADR-006x frontier
that was incorrectly sought on `jpt4/proflog` `main`.

| Artifact | Role |
|----------|------|
| `sources/proflog_pin.json` | Pinned commit and test suites |
| `claims/proflog_sjas_witness.json` | Maps resolved fork blockers to Proflog |
| `sources/proflog_frontier_status.json` | Machine-readable decision |
| `docs/sjas-proflog-crosswalk.md` | Obligation → predicate table |

**Decision:** `authoritative-pinned-executable`

Fast regression (recorded passing): `lein test-proflog-fast` (145 tests).

Extended SJAS regression: `lein test-proflog-sjas` — see
`worked-examples/willard-sjas.md` in the Proflog clone.

## Legacy stub

`jpt4/proflog` `main` remains `do-not-depend-on-public-main` only.

## Verify from AS

```sh
python3 -m autarkic_systems.proflog_integration
python3 -m autarkic_systems.formal_confidence
# Optional live run when AS_PROFLOG_ROOT points at a clone at pinned_commit:
AS_PROFLOG_ROOT=/path/to/proflog python3 -m autarkic_systems.proflog_integration --run-fast
```
