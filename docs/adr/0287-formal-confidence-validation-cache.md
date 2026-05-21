# ADR-0287: Formal Confidence Validation Cache

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0286 made aggregate formal-confidence validation consume the compact
fixed-point construction frontier status. That was the right fail-closed
dependency boundary, but it also put the expensive fixed-point frontier stack
on repeated default formal-confidence and project-status checks.

The fixed-point construction validators already expose process-local cache
telemetry through `cache_clear` and `cache_info`, and their loaded manifest
dataclasses are immutable enough to key the cache. The formal-confidence
target manifest is almost in that shape, except target configuration is loaded
as a mutable `dict`. Repeatedly loaded equivalent default manifests therefore
cannot safely use the same `lru_cache` pattern without making configuration
hashable.

## Decision

Add a process-local cache to `validate_formal_confidence_targets`, using the
same public telemetry convention as the existing fixed-point validators:
`validate_formal_confidence_targets.cache_clear()` and
`validate_formal_confidence_targets.cache_info()`.

Make loaded target configuration immutable and hashable while preserving the
existing mapping-style access used by callers and payload formatters:

- `target.configuration["field"]`;
- `"field" in target.configuration`;
- `target.configuration.items()`; and
- `dict(target.configuration)`.

Cache keys must include the loaded manifest value and the Willard map path, so
a temporary manifest that changes or removes
`fixed_point_construction_frontier_status` receives a separate miss and still
fails closed instead of reusing the checked-in default report.

Do not change the formal-confidence target semantics, proof status, or JSON
payload shape. This ADR is a recomputation guard only.

## Success Criteria

- Red tests fail before implementation because
  `validate_formal_confidence_targets` does not expose `cache_clear` /
  `cache_info`.
- Repeated validation of separately loaded equivalent default
  formal-confidence manifests returns the cached report and increments cache
  hits.
- A temporary manifest with a missing
  `fixed_point_construction_frontier_status` receives a separate cache miss
  and rejects with `target-fixed-point-construction-frontier-status`.
- Existing mapping-style access to `target.configuration` still works.
- Formal-confidence JSON remains accepted for the checked-in target and still
  exposes the accepted ADR-0286 frontier subject.

## Test Plan

- Red:
  `python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_default_formal_confidence_validation_reuses_cached_report_and_tracks_temp_manifest`
- Green:
  `python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_default_formal_confidence_validation_reuses_cached_report_and_tracks_temp_manifest`
- Focused:
  `python -m unittest tests.test_formal_confidence_target tests.test_suite_selection`
- Required aggregate path:
  `python -m unittest tests.test_formal_confidence_target tests.test_project_status_report tests.test_suite_selection`
- Live JSON assertion:
  `python -m autarkic_systems.formal_confidence --format json`
- Parse changed JSON with `python -m json.tool` if JSON changes.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run `python -m autarkic_systems.test_suite_selection --suite fast` if
  runtime permits.

## After Action Report

The targeted red test was:

```sh
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_default_formal_confidence_validation_reuses_cached_report_and_tracks_temp_manifest
```

It failed before implementation because the aggregate validator did not expose
cache telemetry:

```text
AttributeError: 'function' object has no attribute 'cache_clear'
```

The implementation adds `@lru_cache(maxsize=32)` to
`validate_formal_confidence_targets` and makes loaded target configuration a
hashable immutable mapping. Existing mapping-style access and JSON payload
construction are preserved by the mapping adapter.

Focused green verification for the new regression passed:

```sh
time python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_default_formal_confidence_validation_reuses_cached_report_and_tracks_temp_manifest
```

Observed result:

```text
Ran 1 test in 320.359s

OK
```

The test asserts one cold miss for the checked-in default report, a hit for a
separately loaded equivalent default manifest, a separate miss and fail-closed
result for a temp manifest with a missing
`fixed_point_construction_frontier_status`, and a final hit for the default
report.

Additional focused verification passed:

```sh
time python -m unittest tests.test_formal_confidence_target tests.test_suite_selection
```

Observed result:

```text
Ran 30 tests in 1093.469s

OK
```

The requested ADR-0286 aggregate path also passed:

```sh
time python -m unittest tests.test_formal_confidence_target tests.test_project_status_report tests.test_suite_selection
```

Observed result:

```text
Ran 117 tests in 1237.461s

OK
```

The live JSON assertion ran the module CLI, parsed its output, and confirmed
`accepted is True`, `failed_subjects == []`, and the accepted frontier subject
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`:

```text
formal confidence json accepted with fixed_point_construction_frontier_status
```

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite reported manifest `as-test-suite-selection-v1`, suite `fast`,
129 modules, and 1170 tests passed in 263.098s. No JSON files changed in this
slice, so there were no changed JSON files to parse with `json.tool`.
