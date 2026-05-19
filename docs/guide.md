# Guide for new readers

This document orients you to **Autarkic Systems (AS)** after the 2026-05-19 hard
cull. The repository is an **integration layer**: it connects Universal Cell (PRC)
substrate work, formal-confidence boundaries, and **authoritative SJAS proofs in
Proflog**—not a monolithic prover in Python.

## What you are looking at

| Question | Answer |
|----------|--------|
| **Goal** | Theory and machinery toward *cognitive sovereignty*—inspectable logic, implementation, and substrate (see [project-charter.md](project-charter.md)). |
| **Active integration branch** | `culled-main` (charter-focused slice). |
| **Public default branch** | `main` may still be the old scaffold; treat `culled-main` as the current integration baseline until maintainers fast-forward `main`. |
| **Full fork history** | Branch `archive/sean-fork-full` at `09b00f3` — 264 ADRs, Python shadow-SJAS, 11 evidence bundles, meta tooling. |
| **What culled main keeps** | UC runtime, transition claims/proofs, Willard map, slim status, 2 transition + 1 chain evidence bundles, Proflog pin and crosswalk. |
| **What culled main removed** | Python `formal_*` / `substitution_graph_*`, `github_submission`, mega `project_status`, per-ADR evidence multiplication. |

Read [adr/0001-fork-hard-cull.md](adr/0001-fork-hard-cull.md) for policy and success criteria.

## Three programs, two execution venues

```text
                    ┌─────────────────────────────────────┐
                    │     Autarkic Systems (this repo)     │
                    │  integration, claims, evidence, map  │
                    └──────────────┬──────────────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │  jpt4/prc   │         │  jpt4/sjas  │         │ jpt4/afs    │
    │  substrate  │         │  literature │         │ placeholder │
    │  archive    │         │  + nachlass │         │             │
    └──────┬──────┘         └──────┬──────┘         └─────────────┘
           │                       │
           │ UC predicates         │ Willard anchors
           ▼                       ▼
    universal_cell.py      willard_definition_map.json
    evidence bundles              │
                                  ▼
                    ┌─────────────────────────────┐
                    │ autarkenterprises/proflog    │
                    │ SJAS proofs (pinned commit)  │
                    └─────────────────────────────┘
```

- **PRC in AS:** `autarkic_systems/universal_cell.py` implements a **narrow, tested**
  Universal Cell slice (init, write-buffer, neighbor delivery, etc.). Full PRC
  semantics live in [jpt4/prc](https://github.com/jpt4/prc); gaps are listed in
  `sources/command_semantics_gaps.json`.
- **SJAS in AS:** **No** Python proof search. AS holds the Willard integrator map,
  formal-confidence **boundary** (`claims/formal_confidence_boundary.json`), and
  pointers to Proflog. Proofs run in Clojure at the pinned commit.
- **AFS:** Requirements and glossary here; public AFS repo is still a placeholder.

**Do not** reimplement Proflog SJAS in Python without a new ADR.

## Five-minute setup

```sh
git clone https://github.com/jpt4/as.git
cd as
git checkout culled-main   # until merged to main

python3 -m unittest discover
python3 -m autarkic_systems.proflog_integration
python3 -m autarkic_systems.sean_fork_sjas_correlation
python3 -m autarkic_systems.formal_confidence
python3 -m autarkic_systems.project_status --format summary
```

Optional Proflog clone (extended verification):

```sh
git clone https://github.com/autarkenterprises/proflog.git /tmp/proflog-ae
cd /tmp/proflog-ae && git checkout 782f620f3aca951816926bd4d8abba0b40558ede
export AS_PROFLOG_ROOT=/tmp/proflog-ae
cd /path/to/as
python3 -m autarkic_systems.proflog_integration --run-fast
# Sean-fork correlation tests (copy from proflog-contrib/ or run in-tree after copy):
# lein test proflog.as-sean-fork-correlation-test
```

Pin and suite records: `sources/proflog_pin.json`.

## Repository map

| Path | Purpose |
|------|---------|
| `autarkic_systems/` | **Executable core:** `universal_cell.py`, claim/proof checkers, evidence builder, Willard map, `proflog_integration.py`, `sean_fork_sjas_correlation.py`, slim `project_status.py`. |
| `claims/` | Machine-readable claims: transitions, formal-confidence boundary, Proflog witness. |
| `evidence/` | **Culled** bundle registry (2 transition bundles). |
| `evidence/chains/` | One representative multi-hop chain bundle. |
| `sources/` | Pinned manifest, Proflog pin/frontier, PRC maps, command-semantics gaps. |
| `language/` | JSON schemas for transition and chain claim languages (UC layer). |
| `schematics/` | Trace JSON/SVG for exemplar transitions and one chain. |
| `tests/` | Fast Python regression (~185 tests). |
| `docs/adr/` | **Active** ADRs: 0001 cull, 0002 Proflog integration. |
| `docs/correlation/` | Fork distillation index + Sean-fork SJAS→Proflog map. |
| `docs/distillation/` | Human report of fork review (keep/cull/elide). |
| `proflog-contrib/` | Tests/docs to copy into upstream Proflog. |
| `LOG.md` | Chronological development spine (culled era). |
| `MEMORY.md` | High-priority facts for agents/maintainers. |
| `AGENTS.md` | Mandatory dev practices (TDD, ADRs, branches). |

## How claims and proofs work (UC layer)

1. **Claims** — `claims/transition_claims.json` (and chain claims) state what a UC
   transition should achieve.
2. **Proof certificates** — `claims/proof_certificates.json` + ADR-0011 checker
   validate predicate-result proofs over witness traces.
3. **Evidence bundles** — `autarkic_systems/evidence_bundle.py` packages claim,
   proof, schematic trace, and source statuses; registry in `evidence/manifest.json`.
4. **CLI** — `python3 -m autarkic_systems.evidence_bundle --list` (see tests).

SJAS consistency and substitution proofs are **out of scope** for these bundles;
see Proflog crosswalk below.

## SJAS and Proflog (read this before searching for `formal_*.py`)

| Artifact | Role |
|----------|------|
| `sources/proflog_pin.json` | Pinned commit, fast/SJAS suite commands. |
| `sources/proflog_frontier_status.json` | Authoritative vs legacy `jpt4/proflog` stub. |
| `claims/proflog_sjas_witness.json` | Resolved fork blockers. |
| `docs/sjas-proflog-crosswalk.md` | Obligation table (AS vs Proflog). |
| `docs/correlation/sean-fork-sjas-proflog-map.json` | Archive claim → Proflog surface map. |
| `proflog-contrib/` | Re-implementation tests for upstream. |

Sean fork Python validators duplicated Proflog; they were removed on purpose.
To study the old approach: `git checkout archive/sean-fork-full`.

## Documentation tiers

Use [docs/README.md](README.md) as the index. In short:

1. **Start here** — this guide, [project-charter.md](project-charter.md), [glossary.md](glossary.md), [adr-index.md](adr-index.md).
2. **Current integration** — [sjas-proflog-crosswalk.md](sjas-proflog-crosswalk.md), [proof-apparatus-options.md](proof-apparatus-options.md), [open-problems.md](open-problems.md), [roadmap.md](roadmap.md).
3. **UC reference** — [transition-claim-language.md](transition-claim-language.md), [prc-hardware-witness-map.md](prc-hardware-witness-map.md), [willard-definition-map.md](willard-definition-map.md).
4. **Historical fork slices** — many `docs/*-status.md` files describe ADR-scoped
   work preserved in code or archive; see [historical-fork-docs.md](historical-fork-docs.md).
5. **Distillation** — [distillation/fork-correlation.md](distillation/fork-correlation.md) explains the Sean fork review.

## Branches and git workflow

| Branch | Use |
|--------|-----|
| `culled-main` | Current charter-focused integration. |
| `main` | Upstream default; may lag until merge. |
| `archive/sean-fork-full` | Read-only snapshot of full fork. |
| `distill/fork-correlation` | Distillation work branch (historical). |

Per `AGENTS.md`: ADR before features, branch per ADR, local merge to `main` then
push; preserve feature branches.

## Common tasks

| Task | Where to look |
|------|----------------|
| Add a UC transition claim | ADR → `transition_claims.json` → tests → optional evidence bundle. |
| Check formal confidence | `claims/formal_confidence_boundary.json`, `python3 -m autarkic_systems.formal_confidence`. |
| Unblock SJAS work | Do **not** add Python provers; extend Proflog, update pin/witness/crosswalk. |
| Map fork SJAS to Proflog | `docs/correlation/sean-fork-sjas-proflog-map.json`, `sean_fork_sjas_correlation` module. |
| Command semantics gap | `sources/command_semantics_gaps.json`, `project_status`. |
| Full ADR history | `git checkout archive/sean-fork-full -- docs/adr/`. |

## Related repositories

Machine-readable: `sources/manifest.json`, `docs/correlation/subordinate-manifest.json`.

| Repo | Relationship |
|------|----------------|
| [jpt4/prc](https://github.com/jpt4/prc) | Subordinate substrate archive. |
| [jpt4/sjas](https://github.com/jpt4/sjas) | Subordinate logic/literature. |
| [jpt4/afs](https://github.com/jpt4/afs) | Subordinate placeholder. |
| [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) | **Authoritative** SJAS implementation. |
| [jpt4/proflog](https://github.com/jpt4/proflog) | Legacy stub — do not use for ADR-006x. |

## What to read next

1. [project-charter.md](project-charter.md) — intent and scope.
2. [adr/0002-proflog-integration-unblocks-sjas.md](adr/0002-proflog-integration-unblocks-sjas.md) — why SJAS left Python.
3. [distillation/fork-correlation.md](distillation/fork-correlation.md) — fork keep/cull verdicts.
4. `autarkic_systems/universal_cell.py` — executable UC entry point.

For agent/maintainer constraints, see root `AGENTS.md` and `MEMORY.md`.
