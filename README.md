# Autarkic Systems

Integration repository for **cognitive sovereignty**: connecting Autarkic Formal
Systems (AFS), Pervasively Reconfigurable Computing (PRC), and Self-Justifying
Axiom Systems (SJAS).

**New here?** Read **[docs/guide.md](docs/guide.md)** — branches, layout, what was
culled, and how UC work relates to Proflog.

## Current baseline

| Item | Value |
|------|--------|
| Integration branch | `culled-main` (charter-focused; merge to `main` pending) |
| Full fork archive | `archive/sean-fork-full` @ `09b00f3` (264 ADRs) |
| PRC in AS | `autarkic_systems/universal_cell.py` + 2 transition evidence bundles |
| SJAS proofs | [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) pinned @ `782f620` — not reimplemented in Python |
| Formal confidence | `integrated` — see `claims/formal_confidence_boundary.json` |

## Verify (fast)

```sh
python3 -m unittest discover
python3 -m autarkic_systems.proflog_integration
python3 -m autarkic_systems.sean_fork_sjas_correlation
python3 -m autarkic_systems.formal_confidence
python3 -m autarkic_systems.project_status --format summary
```

Extended: clone Proflog at `sources/proflog_pin.json`, set `AS_PROFLOG_ROOT`, run
`python3 -m autarkic_systems.proflog_integration --run-fast` and
`lein test-proflog-sjas`.

## Layout

| Path | Role |
|------|------|
| `autarkic_systems/` | UC runtime, claims, evidence, Willard map, Proflog/correlation validators |
| `claims/` | Transition claims, formal-confidence boundary, Proflog witness |
| `evidence/` | Culled bundle registry (2 transition + 1 chain) |
| `sources/` | Manifest, Proflog pin, PRC maps, command-semantics gaps |
| `docs/` | [Documentation index](docs/README.md), [reader guide](docs/guide.md), ADRs |
| `proflog-contrib/` | Sean-fork SJAS tests to copy into upstream Proflog |
| `tests/` | Fast Python regression |

## Charter and practices

- [docs/project-charter.md](docs/project-charter.md)
- [AGENTS.md](AGENTS.md) — TDD, ADRs, branch discipline
- [docs/adr-index.md](docs/adr-index.md) — active vs archived decisions
