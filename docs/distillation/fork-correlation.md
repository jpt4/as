# Fork distillation and correlation report

Date: 2026-05-19

## Mandate

Per `distillation-and-correlation.txt`, review the fork
[Sean-Kenneth-Doherty/as](https://github.com/Sean-Kenneth-Doherty/as), extract
useful contributions against Autarkic Systems objectives, correlate duplicates
with work in AFS/PRC/SJAS/Proflog, and land a selective merge on branch
`distill/fork-correlation` for periodic refresh as the fork updates.

Upstream context: [jpt4/as#1](https://github.com/jpt4/as/issues/1) documents
write-access denial to the fork author; fork `main` at `8dc90a83` is 264 commits
ahead of origin scaffold `1a2fc06`.

## Executive summary

The fork is **substantive and on-mission**. It is not a stray experiment: it
implements the ADR-scaffolded AS programme end-to-end—orientation, PRC-linked
Universal Cell evidence, proof certificates, and a growing Willard/SJAS
formal-confidence stack—using the discipline in `AGENTS.md`.

**Selective merge decision:** import fork `main` wholesale onto
`distill/fork-correlation`, then apply **correlation corrections** (below)
before any fast-forward to `jpt4/as` `main`. Do not treat fork-only
publication tooling as canonical project memory.

**Critical correction (applied on `culled-main`):** fork ADR-0014 correctly refused
`jpt4/proflog` `main`, but implied the SJAS ADR-006x frontier was *lost*.
That frontier is on [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog)
at `14d3150`. AS now pins it (`sources/proflog_pin.json`), records resolved
blockers (`claims/proflog_sjas_witness.json`), and sets formal-confidence to
`integrated` with SJAS delegated to Proflog — see ADR-0002.

## What the fork contributes (by AS pillar)

### Integrative structure (AFS)

- Project charter, glossary, AFS requirements, literature map, open problems,
  roadmap, 263 ADRs with AARs.
- Pinned `sources/manifest.json` and repeatable review discipline.

**Correlation:** `jpt4/afs` remains a placeholder; this work *is* the current
AFS integrator until AFS gains its own codebase.

### Embodied substrate (PRC)

- `autarkic_systems/universal_cell.py`: stem/recipient command paths through
  init, write-buffer, neighbor delivery, multi-command rejection.
- Eleven transition evidence bundles, two chain bundles, one network-sequence
  bundle; schematic traces and SVGs.
- Source-status JSON for command-token blockers with resolution-question
  discipline (project status schema 22).

**Correlation:** Grounded in PRC `7e82c73` formal model and legacy simulators;
does not duplicate full PRC. Hardware witness map (ADR-0015+) links AS claims
to PRC schematics without claiming fab-ready design.

### Formal confidence (SJAS)

- Willard definition map and machine-checked anchors.
- Formal arithmetic language, codebook, substitution, quotation, diagonal seed,
  substitution-graph targets/correctness cases, fixed-point construction case
  map (ADR-0226–0264).
- `AS-FORMAL-CONFIDENCE-TARGET-001` explicitly blocked on
  `fixed-point-construction`—honest boundary, not false progress.

**Correlation:** Parallel to
`autarkenterprises/proflog` `willard_sjas` / `subst` / worked-examples; AS
artifacts are **target and evidence boundaries in Python**, not a second
Proflog. Future integration should cross-walk claim IDs, not merge codebases
without ADR.

### Proof apparatus

- ADR-0010: AS-local `predicate-result` certificates (52 steps).
- ADR-0014: blocked public Scheme stub—**scope corrected** in this
  distillation to distinguish stub vs authoritative Proflog.

## Proflog: correcting the fork misconception

| Repository | Role | ADR-006x frontier | AS stance |
|------------|------|-------------------|-----------|
| `jpt4/proflog` `main` | Legacy Fitting Scheme sketch | Absent | Background only; Guile smoke fails; **do not depend** |
| `autarkenterprises/proflog` `main` | Greenfield SJAS implementation | Present (`tableau-proof/3`, `subst-prf/4`, `subst-code/2`, SelfCons checks in `worked-examples/willard-sjas.md`) | **Authoritative reference**; not finalized; defer *runtime* dependency per ADR-0010 until integration ADR |

The fork's P6 "recover or replace" problem is reframed: **recover** means pin
and cross-reference `autarkenterprises/proflog`, not hunt for unpublished ADR
source. **Replace** remains valid only if that repository is abandoned.

Updated artifacts on this branch:

- `sources/proflog_frontier_status.json` (schema 2)
- `docs/proflog-frontier-status.md`
- `docs/correlation/subordinate-manifest.json`

## Extraneous or meta material (summarized, not imported to MEMORY)

| Material | Verdict |
|----------|---------|
| `github_submission.py`, `handoff.py`, submission ADRs | Useful operator tooling for fork→origin promotion; keep in repo, summarize only in distillation docs |
| `AGENTS.md~` | Scratch backup; **removed** on this branch |
| Developer paths `/home/sean/Projects/_upstream/*` | Environment-specific; noted in correlation manifest for later env-var ADR |
| Extremely long `README.md` | Valid navigational index; acceptable; do not duplicate in MEMORY |

## Duplicate content map

See `docs/correlation/subordinate-manifest.json` for machine-readable entries.
High-signal duplicates:

1. **Willard anchors** — AS JSON map ↔ Proflog worked examples ↔ SJAS papers.
2. **Substitution graph / diagonal** — AS Python validators ↔ Proflog relational code.
3. **UC transitions** — AS predicates ↔ PRC Scheme simulators (subset).

## Integration workflow (ongoing)

1. Fetch `Sean-Kenneth-Doherty/as` (`git fetch` → `refs/remotes/fork/*`).
2. Diff `fork/main` against `distill/fork-correlation`.
3. Merge new ADR slices; re-run correlation notes for Proflog/PRC heads.
4. When accepted, fast-forward `main` locally per AGENTS.md branch discipline
   (no PR-merge trigger).

## Verification note

Fork documentation claims `python -m unittest discover` passes (46+ tests at
issue filing; 131 test modules at ADR-0264). This environment uses `python3`;
full `discover` did not complete within a bounded timeout here—run locally
before promoting to `main`. Focused `tests.test_proflog_frontier_status` passes
after schema-2 update.

## Next integration slices (recommended)

1. ADR to pin `autarkenterprises/proflog` in `sources/manifest.json` with CI
   clone or submodule policy.
2. Cross-index `AS-SUBSTITUTION-GRAPH-*` targets to Proflog predicate names.
3. Normalize upstream test paths away from `/home/sean/...`.
4. Fast-forward `main` from `distill/fork-correlation` when maintainers approve.
