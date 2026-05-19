# Development Log

## 2026-05-19 - Proflog integration unblocks SJAS (ADR-0002)

- Pinned autarkenterprises/proflog at `14d3150`; fast suite `lein test-proflog-fast`
  recorded passing (145 tests).
- Added `sources/proflog_pin.json`, `claims/proflog_sjas_witness.json`,
  `autarkic_systems/proflog_integration.py`.
- Changed `AS-FORMAL-CONFIDENCE-TARGET-001` to `integrated`; former Proflog
  blockers documented as resolved via authoritative repo, not Python reimplementation.
- Updated `sources/proflog_frontier_status.json` decision to
  `authoritative-pinned-executable`; P6 closed in `docs/open-problems.md`.

## 2026-05-19 - Sean fork hard cull (ADR-0001)

- Created `archive/sean-fork-full` at `09b00f3` preserving 264 ADRs and full fork.
- Branch `culled-main`: removed Python shadow-SJAS stack, meta reporting
  (`project_status` mega-module, `github_submission`, `handoff`, demos), and
  per-slice evidence/schematic multiplication.
- Kept UC runtime, claim/proof surfaces, Willard map, Proflog authoritative
  reference, two transition evidence bundles, one chain bundle, merged
  `sources/command_semantics_gaps.json`.
- See [docs/adr/0001-fork-hard-cull.md](docs/adr/0001-fork-hard-cull.md) and
  [docs/adr-index.md](docs/adr-index.md).

## Earlier history

Full chronological log through ADR-0264 is on branch `archive/sean-fork-full`.
