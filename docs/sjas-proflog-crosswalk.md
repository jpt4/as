# SJAS / Proflog crosswalk

Status: 2026-05-19 — blockers resolved via pin at `782f620` (includes Sean-fork correlation tests).

[autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) is the
authoritative SJAS implementation. AS does not duplicate this machinery in Python.

## Former fork blockers → Proflog resolution

| Former blocker | Proflog resolution |
|----------------|-------------------|
| Missing ADR-006x on `jpt4/proflog` main | Full surface on `autarkenterprises/proflog` `main` |
| Fixed-point construction | `worked-examples/willard-sjas.md` ADR-0065–0071 |
| Substitution graph / representability | `subst-code/2`, `subst-prf/4`, `subst.clj` |
| Deduction apparatus (SJAS) | `tableau-proof/3`, kernel profiles in `willard_sjas.clj` |
| Self-consistency claim in AS Python | **Not claimed in AS** — witness in Proflog tests |

Machine-readable witness: `claims/proflog_sjas_witness.json`.

Sean fork translation map (archive `archive/sean-fork-full` → Proflog):
`docs/correlation/sean-fork-sjas-proflog-map.json`. Re-implementation tests live in
`proflog-contrib/test/proflog/as_sean_fork_correlation_test.clj` (verified at pin).

## Obligation map

| AS obligation | Proflog surface |
|---------------|-----------------|
| Level-1 consistency | `:willard-sjas-level1`, SelfCons checks |
| Substitution | `subst-code/2`, `subst-prf/4` |
| Tableau proofs | `tableau-proof/3` |
| Code / syntax | `willard_sjas_code.clj`, structural decoder ADR-0067 |
| UC substrate | `autarkic_systems/universal_cell.py` (AS only) |

## Verification

| Suite | Command | AS default path |
|-------|---------|-----------------|
| Fast | `lein test-proflog-fast` | Recorded pass in `sources/proflog_pin.json` |
| SJAS | `lein test-proflog-sjas` | Extended suite |
| SJAS slow | `lein test-proflog-sjas-slow` | Extended suite |
