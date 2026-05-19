# Project Memory

- Autarkic Systems integrates AFS, PRC, and SJAS toward cognitive sovereignty.
- **Culled main** (`culled-main`): charter-focused; full Sean fork on
  `archive/sean-fork-full` at `09b00f3`.
- **PRC:** `autarkic_systems/universal_cell.py` implements a tested UC slice; not
  full `jpt4/prc` parity. Command gaps: `sources/command_semantics_gaps.json`.
- **SJAS:** [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog)
  is authoritative (`14d3150`). `jpt4/proflog` main is legacy stub only.
  No Python `formal_*` / `substitution_graph_*` on culled main.
- **Formal confidence:** `integrated` — UC in AS, SJAS in pinned Proflog
  (`sources/proflog_pin.json`, `claims/proflog_sjas_witness.json`).
- **Evidence:** Two transition bundles in `evidence/manifest.json`; one chain
  bundle in `evidence/chains/manifest.json`.
- **Reader guide:** `docs/guide.md`; doc index `docs/README.md`.
- Default branch: `main` (may lag); active work on `culled-main`. Integration uses
  local merge then push per `AGENTS.md`.
