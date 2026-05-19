# ADR-0002: Proflog Integration Unblocks SJAS

Date: 2026-05-19

Status: Accepted

## Context

ADR-0014 and subsequent formal-confidence ADRs blocked on a missing Proflog
ADR-006x frontier visible only on `jpt4/proflog` `main`. That stub is not the
authoritative SJAS implementation.

## Decision

Pin [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) at
`14d3150ed3a8029347b8981d657a22a1efde2753` and record:

- `sources/proflog_pin.json` — pin and fast-suite witness
- `claims/proflog_sjas_witness.json` — resolved fork blockers
- `autarkic_systems.proflog_integration` — validation CLI
- `AS-FORMAL-CONFIDENCE-TARGET-001` status `integrated` (SJAS delegated to Proflog)

## Success Criteria

- `python3 -m autarkic_systems.proflog_integration` accepts
- `python3 -m autarkic_systems.formal_confidence` accepts with status `integrated`
- P6 in `docs/open-problems.md` marked resolved
