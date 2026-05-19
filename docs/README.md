# Documentation index

Navigation for the culled Autarkic Systems tree. **New readers:** start with
[guide.md](guide.md).

## Tier 1 — Start here

| Document | Description |
|----------|-------------|
| [guide.md](guide.md) | **Primary onboarding:** branches, layout, UC vs SJAS, verification. |
| [project-charter.md](project-charter.md) | Purpose, subsumed programs, deliverables. |
| [glossary.md](glossary.md) | Terms (UC, automail, formal confidence, …). |
| [adr-index.md](adr-index.md) | Active ADRs vs archive; what survived the cull. |

## Tier 2 — Current integration

| Document | Description |
|----------|-------------|
| [sjas-proflog-crosswalk.md](sjas-proflog-crosswalk.md) | AS obligations ↔ Proflog surfaces. |
| [proof-apparatus-options.md](proof-apparatus-options.md) | UC certificates vs Proflog SJAS. |
| [proflog-frontier-status.md](proflog-frontier-status.md) | Authoritative repo vs legacy stub. |
| [open-problems.md](open-problems.md) | Ranked open problems (P6 Proflog closed). |
| [roadmap.md](roadmap.md) | Near-term priorities. |
| [afs-requirements.md](afs-requirements.md) | AFS requirement matrix (archive ADR refs; see banner). |
| [source-manifest.md](source-manifest.md) | How to read `sources/manifest.json`. |

## Tier 3 — UC / PRC reference

| Document | Description |
|----------|-------------|
| [transition-claim-language.md](transition-claim-language.md) | Transition claim JSON language. |
| [prc-hardware-witness-map.md](prc-hardware-witness-map.md) | Hardware witness mapping. |
| [willard-definition-map.md](willard-definition-map.md) | Willard anchor integrator. |
| [stem-command-buffer-map.md](stem-command-buffer-map.md) | Stem command buffer map. |

## Tier 4 — Correlation and distillation

| Path | Description |
|------|-------------|
| [correlation/subordinate-manifest.json](correlation/subordinate-manifest.json) | Subordinate repo correlation index. |
| [correlation/sean-fork-sjas-proflog-map.json](correlation/sean-fork-sjas-proflog-map.json) | Sean fork SJAS → Proflog translation map. |
| [distillation/README.md](distillation/README.md) | Distillation directory overview. |
| [distillation/fork-correlation.md](distillation/fork-correlation.md) | Fork review report (keep/cull/elide). |

## Tier 5 — Historical fork slice docs

These files document **ADR-scoped slices** from the Sean fork integration line.
On `culled-main`, related Python modules or per-slice evidence may be **removed**
while the markdown remains as design context. See
[historical-fork-docs.md](historical-fork-docs.md) for status per file.

Examples: `write-buffer-command-semantics-status.md`, `vertical-demo-digest.md`,
`post-handoff-signal-witness.md`, `subordinate-review.md`.

## Active ADRs (culled main)

| ADR | Title |
|-----|-------|
| [adr/0001-fork-hard-cull.md](adr/0001-fork-hard-cull.md) | Hard-cull policy and archive pointer. |
| [adr/0002-proflog-integration-unblocks-sjas.md](adr/0002-proflog-integration-unblocks-sjas.md) | Proflog pin; SJAS blockers resolved. |

Full ADR sequence (0001–0264): branch `archive/sean-fork-full`.

## Root-level docs outside `docs/`

| File | Role |
|------|------|
| `/README.md` | Repository entry point. |
| `/LOG.md` | Chronological development log. |
| `/MEMORY.md` | Persistent high-priority facts. |
| `/AGENTS.md` | Agent and contributor practices. |
| `/distillation-and-correlation.txt` | Original distillation mandate. |
