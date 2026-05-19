# Autarkic Systems

Umbrella project for cognitive sovereignty: integrating Autarkic Formal Systems,
Pervasively Reconfigurable Computing (PRC), and Self-Justifying Axiom Systems (SJAS).

## Charter

See [docs/project-charter.md](docs/project-charter.md) and [AGENTS.md](AGENTS.md).

## Current state (culled main)

- **PRC:** Narrow Universal Cell implementation in
  `autarkic_systems/universal_cell.py` with claim/proof certificates and two
  representative [evidence bundles](evidence/manifest.json).
- **SJAS:** Willard anchor map + integrator boundary; proofs in
  [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog) — see
  [docs/sjas-proflog-crosswalk.md](docs/sjas-proflog-crosswalk.md).
- **Archive:** Full Sean fork (264 ADRs) on branch `archive/sean-fork-full`.

## Verify

```sh
python3 -m unittest discover
python3 -m autarkic_systems.proflog_integration
python3 -m autarkic_systems.formal_confidence
python3 -m autarkic_systems.project_status --format summary
```

Extended: `lein test-proflog-sjas` in a clone at `sources/proflog_pin.json`
commit; set `AS_PROFLOG_ROOT` for live `proflog_integration --run-fast`.

## Layout

| Path | Role |
|------|------|
| `autarkic_systems/` | UC runtime, claims, evidence, Willard map, status |
| `claims/` | Transition claims, formal-confidence boundary |
| `evidence/` | Bundle registry (culled) |
| `sources/` | Manifest, PRC maps, Proflog status, command gaps |
| `docs/` | Charter, literature, ADR index, crosswalk |
| `tests/` | Fast regression suite |
