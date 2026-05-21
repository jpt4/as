# ADR-0290: Substitution Graph Correctness Frontier Validation Cache

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0274 added the compact substitution graph correctness frontier status.
ADR-0285 then made the fixed-point construction frontier consume that status
as one of its compact construction-case handoffs. The validator therefore sits
on a repeated aggregate path: direct substitution-graph checks, fixed-point
frontier checks, formal-confidence checks, project-status checks, and handoff
checks can all ask for the same default report in one process.

The adjacent fixed-point and formal-confidence validators already expose
process-local `lru_cache` telemetry through `cache_clear` and `cache_info`.
The substitution graph correctness frontier validator does not yet expose that
convention, and its loaded manifest includes a mutable `dict` in
`case_status_paths`. That mutable mapping prevents the loaded manifest from
being a safe cache key even though the validator should be able to reuse two
separately loaded but equivalent default manifests.

Any cache must remain fail-closed. A temporary manifest that changes or omits a
case-status path must be a separate cache miss, reject under the existing
case-status path/load checks, and leave the checked-in default report reusable
afterwards.

## Decision

Add a process-local cache to
`validate_substitution_graph_correctness_frontier_status`, using the same
public telemetry convention as the existing cached validators:
`validate_substitution_graph_correctness_frontier_status.cache_clear()` and
`validate_substitution_graph_correctness_frontier_status.cache_info()`.

Make loaded `case_status_paths` immutable and hashable while preserving the
mapping access and payload behavior already used by callers:

- `manifest.case_status_paths["case-kind"]`;
- `manifest.case_status_paths.get("case-kind")`;
- `"case-kind" in manifest.case_status_paths`;
- `manifest.case_status_paths.items()`; and
- `dict(manifest.case_status_paths)`.

Cache keys must include the full loaded manifest value, including the manifest
path and the immutable case-status path mapping. Equivalent checked-in
manifests therefore reuse one report, while temporary or changed manifests keep
separate cache entries and still fail closed.

Do not change frontier semantics, report payload shape, text format, blockers,
proof status, fixed-point semantics, or formal-confidence semantics. This ADR
is a recomputation guard only.

## Success Criteria

- Red tests fail before implementation because
  `validate_substitution_graph_correctness_frontier_status` does not expose
  `cache_clear` / `cache_info`.
- Repeated validation of separately loaded equivalent default substitution
  graph correctness frontier manifests returns the cached report and increments
  cache hits.
- Existing mapping-style access to `case_status_paths` still works.
- A temporary manifest with a changed or missing case-status path receives a
  separate cache miss and rejects under the existing fail-closed
  case-status-path or case-status-load subjects.
- The checked-in default cached report remains valid and reusable after the
  temporary manifest rejection.
- The live JSON payload remains accepted with no failed subjects, five compact
  case statuses, and five accepted compact case statuses.

## Test Plan

- Red:
  `python -m unittest tests.test_substitution_graph_correctness_frontier_status.SubstitutionGraphCorrectnessFrontierStatusTests.test_default_frontier_status_validation_reuses_cached_report_and_tracks_temp_manifest`.
- Green:
  `python -m unittest tests.test_substitution_graph_correctness_frontier_status.SubstitutionGraphCorrectnessFrontierStatusTests.test_default_frontier_status_validation_reuses_cached_report_and_tracks_temp_manifest`.
- Focused:
  `python -m unittest tests.test_substitution_graph_correctness_frontier_status tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.substitution_graph_correctness_frontier_status --format json`.
- Parse changed JSON with `python -m json.tool` if JSON files change.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run `python -m autarkic_systems.test_suite_selection --suite fast` if
  runtime permits.

## After Action Report

The targeted red test was:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status.SubstitutionGraphCorrectnessFrontierStatusTests.test_default_frontier_status_validation_reuses_cached_report_and_tracks_temp_manifest
```

It failed before implementation because the aggregate validator did not expose
cache telemetry:

```text
AttributeError: 'function' object has no attribute 'cache_clear'

Ran 1 test in 0.001s
FAILED (errors=1)
```

The implementation adds `@lru_cache(maxsize=32)` to
`validate_substitution_graph_correctness_frontier_status` and makes loaded
`case_status_paths` a hashable immutable mapping. Existing mapping-style access
and JSON payload construction are preserved by the mapping adapter.

The exact red test then passed:

```text
Ran 1 test in 7.485s
OK
```

The regression asserts one cold miss for the checked-in default report, a hit
for a separately loaded equivalent default manifest, a separate miss and
fail-closed result for a temp manifest with a missing compact case-status path,
and a final hit for the default report.

Focused verification passed:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status tests.test_suite_selection
```

Observed result:

```text
Ran 23 tests in 52.658s
OK
```

The live JSON assertion ran the module CLI, parsed its output, and confirmed
`accepted is True`, `failed_subjects == []`, `case_status_count == 5`, and
`accepted_case_status_count == 5`:

```text
substitution graph correctness frontier json accepted 5 5
```

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
python -m autarkic_systems.test_suite_selection --suite fast
```

`compileall` completed in 0.816s. The fast suite reported manifest
`as-test-suite-selection-v1`, suite `fast`, 129 modules, and 1171 tests passed
in 236.708s. No JSON files changed in this slice, so there were no changed JSON
files to parse with `json.tool`.

This is a recomputation guard only. It does not change substitution graph
correctness frontier semantics, report payload shape, text format, blockers,
proof status, fixed-point semantics, or formal-confidence semantics.
