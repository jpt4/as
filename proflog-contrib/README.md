# Proflog upstream contribution: Sean fork SJAS correlation

These files translate Sean fork AS SJAS artifacts (on `archive/sean-fork-full`)
into tests and documentation for [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog).

## Upstream status

Landed on `autarkenterprises/proflog` `main` at `782f620` (2026-05-19). The
`proflog-contrib/` tree mirrors upstream for AS review; prefer the pinned commit
in `sources/proflog_pin.json`.

## Verify

```sh
export AS_PROFLOG_ROOT=/path/to/proflog   # checkout at pinned commit
lein test proflog.as-sean-fork-correlation-test
```

## AS-side correlation

Machine-readable map: `docs/correlation/sean-fork-sjas-proflog-map.json`

Validation: `python3 -m autarkic_systems.sean_fork_sjas_correlation`
