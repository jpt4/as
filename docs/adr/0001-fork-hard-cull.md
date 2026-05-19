# ADR-0001: Sean Fork Hard Cull

Date: 2026-05-19

Status: Accepted

## Context

The Sean-Kenneth-Doherty fork added 264 ADRs and a large Python surface that
partially duplicates [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog)
while manufacturing formal-confidence progress through JSON validators. The
fork also added substantial but narrow PRC Universal Cell implementation that
advances the AS charter.

Full fork history is preserved on branch `archive/sean-fork-full` at
`09b00f38a50db9905dd9cbe17590b5a6ee65fda1`.

## Decision

Hard-cull `culled-main` to charter-focused integration:

1. **Keep** UC runtime, claim/proof surfaces, minimal evidence framework, Willard
   anchor map, Proflog authoritative reference, and merged command-semantics gaps.
2. **Remove** Python shadow-SJAS stack (`formal_*`, `substitution_graph_*`,
   `fixed_point_*` validators except obstruction note), meta reporting
   (`project_status` mega-module, `github_submission`, `handoff`, demos), and
   264 micro-ADRs from main (index only on main; full tree on archive branch).
3. **Replace** SJAS proof work with Proflog pin + `docs/sjas-proflog-crosswalk.md`.

## Success Criteria

- `archive/sean-fork-full` exists on remote at `09b00f3`.
- No `substitution_graph_*` or `formal_*` modules on `culled-main`.
- README under 120 lines; `docs/adr/` contains only this ADR plus `docs/adr-index.md`.
- `python3 -m unittest discover` passes on fast path.
- At least two transition evidence bundles remain with working cross-layer validation.

## Failure Criteria

- UC regression cannot be preserved without restoring removed ceremony; stop and
  document on archive branch.
- Formal-confidence boundary cannot be stated without Proflog crosswalk.

## Consequences

- Main line is integrator-focused; historical ADR granularity lives on archive branch.
- Sean fork authors should treat `archive/sean-fork-full` as audit trail, not main.

## After Action Report

(To be updated when cull lands on `culled-main`.)
