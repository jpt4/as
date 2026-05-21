# ADR-0286: Formal Confidence Fixed-Point Frontier Dependency

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0263 made the aggregate formal-confidence target depend on the raw
fixed-point construction case map. That was correct for the first decomposition
of the remaining `fixed-point-construction` blocker, because the case map
showed that all five construction cases were explicit and still open.

ADR-0273 then added a compact aggregate fixed-point construction frontier
status. ADR-0285 extended that aggregate status with a compact
`case_status_rollup` over the five construction-case status handoffs. The
frontier status now says more than the raw case map: it checks the seven finite
support surfaces, rolls up all five compact case-status reports, confirms that
all five rollups accept, and preserves that the aggregate construction frontier
is still blocked by `fixed-point-construction`.

The formal-confidence target is currently behind that frontier. It still
accepts or rejects based on the raw construction case map alone. That leaves a
gap: one compact case-status handoff could drift, reject, or claim a closed
proof boundary while the aggregate formal-confidence validator remains green.

## Decision

Add a required `fixed_point_construction_frontier_status` configuration field
to `claims/formal_confidence_targets.json`, pointing at
`claims/fixed_point_construction_frontier_status.json`.

Update `autarkic_systems.formal_confidence` so aggregate formal-confidence
validation loads and validates
`autarkic_systems.fixed_point_construction_frontier_status`. The dependency is
accepted only when the compact frontier status report accepts, reports
`frontier_status` as `blocked`, remains blocked by
`fixed-point-construction`, and exposes five accepted compact construction-case
status rollups.

Keep the existing `fixed_point_construction_cases` dependency. The raw case map
is still useful as the direct decomposition of the construction blocker; the
compact frontier status is now an additional handoff that validates the
case-status rollups and support surfaces without claiming the fixed point.

Documentation should describe the formal-confidence target as consuming the
compact fixed-point construction frontier handoff with five accepted
case-status rollups while still not claiming a fixed-point equation or
self-consistency theorem.

## Success Criteria

- Red tests fail before implementation because formal-confidence validation
  does not require or validate `fixed_point_construction_frontier_status`.
- The checked-in formal-confidence target manifest names
  `claims/fixed_point_construction_frontier_status.json`.
- Formal-confidence validation fails closed when the frontier status path is
  missing, invalid, no longer accepted, no longer blocked, no longer blocked by
  `fixed-point-construction`, or no longer reports five accepted case-status
  rollups.
- JSON payload and text output expose an accepted validation subject for
  `fixed_point_construction_frontier_status`.
- The existing `fixed_point_construction_cases` dependency remains in place.
- Documentation states that the compact fixed-point construction frontier
  handoff is consumed without promoting the fixed point.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target`.
- Green: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.formal_confidence --format json`.
- Parse `claims/formal_confidence_targets.json` with `python -m json.tool`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- If runtime permits, run
  `python -m autarkic_systems.test_suite_selection --suite fast`.

## After Action Report

The first full red attempt against `tests.test_formal_confidence_target` was
stopped after it spent several minutes repeating expensive fixed-point
validation. The targeted red test preserved the intended TDD signal:

```sh
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_checked_in_target_names_current_formal_confidence_boundary
```

It failed because `REQUIRED_CONFIGURATION_FIELDS` did not yet include
`fixed_point_construction_frontier_status`:

```text
AssertionError: Tuples differ
First differing element 17:
'fixed_point_obstruction'
'fixed_point_construction_frontier_status'
```

The implementation adds the required configuration field, points the checked
formal-confidence manifest at
`claims/fixed_point_construction_frontier_status.json`, and updates
`autarkic_systems.formal_confidence` to load and validate the compact
frontier status report. The new dependency accepts only when the frontier
report accepts, remains `blocked`, remains blocked by
`fixed-point-construction`, and exposes five accepted construction-case status
rollups. The existing raw `fixed_point_construction_cases` dependency remains
in place.

Focused green verification:

```sh
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_checked_in_target_names_current_formal_confidence_boundary
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_checked_in_target_validates_against_willard_map
python -m unittest tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_missing_fixed_point_construction_frontier_status_is_rejected tests.test_formal_confidence_target.FormalConfidenceTargetTests.test_promoted_fixed_point_construction_frontier_status_is_rejected
python -m unittest tests.test_formal_confidence_target tests.test_project_status_report tests.test_suite_selection
```

Observed results:

- boundary target test: 1 test passed;
- checked-in validation test: 1 test passed in 322.073s;
- missing/promoted frontier-status tests: 2 tests passed in 341.632s; and
- required focused suite: 116 tests passed in 2629.104s.

The live JSON assertion was:

```sh
python - <<'PY'
import json
import subprocess
import sys

completed = subprocess.run(
    [sys.executable, "-m", "autarkic_systems.formal_confidence", "--format", "json"],
    cwd=".",
    capture_output=True,
    text=True,
    check=False,
)
if completed.returncode != 0:
    print(completed.stdout)
    print(completed.stderr, file=sys.stderr)
    raise SystemExit(completed.returncode)
payload = json.loads(completed.stdout)
assert payload["accepted"] is True, payload
assert payload["failed_subjects"] == [], payload["failed_subjects"]
subject = "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status"
assert any(
    result["subject"] == subject and result["accepted"] is True
    for result in payload["results"]
), payload["results"]
print("formal confidence json accepted with fixed_point_construction_frontier_status")
PY
```

It printed:

```text
formal confidence json accepted with fixed_point_construction_frontier_status
```

Additional verification passed:

```sh
python -m json.tool claims/formal_confidence_targets.json >/dev/null
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite reported manifest `as-test-suite-selection-v1`, suite `fast`,
129 modules, and 1170 tests passed in 355.356s.

This remains a dependency/status handoff only. It does not prove or promote
substitution representability, substitution graph correctness, bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.
