# Proflog upstream contribution: Sean fork SJAS correlation

These files translate Sean fork AS SJAS artifacts (on `archive/sean-fork-full`)
into tests and documentation for [autarkenterprises/proflog](https://github.com/autarkenterprises/proflog).

## Apply to Proflog

```sh
export PROFLOG_ROOT=/path/to/proflog   # checkout at sources/proflog_pin.json commit
cp -r proflog-contrib/test/proflog/as_sean_fork_correlation_test.clj \
  "$PROFLOG_ROOT/test/proflog/"
cp proflog-contrib/worked-examples/as-sean-fork-correlation.md \
  "$PROFLOG_ROOT/worked-examples/"
# Add to project.clj test selectors if desired:
#   :as-sean-fork-correlation (complement :slow) ...
lein test :as-sean-fork-correlation
```

## AS-side correlation

Machine-readable map: `docs/correlation/sean-fork-sjas-proflog-map.json`

Validation: `python3 -m autarkic_systems.sean_fork_sjas_correlation`
