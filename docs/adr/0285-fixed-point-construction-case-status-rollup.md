# ADR-0285: Fixed-Point Construction Case Status Rollup

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0273 added a compact aggregate status surface for the fixed-point
construction frontier. That surface loads the five construction cases, checks
the raw finite support surfaces that make the cases actionable, and preserves
the aggregate `fixed-point-construction` blocker.

ADR-0275 through ADR-0278 and ADR-0284 then added compact status handoffs for
all five construction cases:

- `substitution-representability-proof`;
- `substitution-graph-correctness-proof`;
- `bridge-equality-proof`;
- `diagonal-instance-closure`; and
- `fixed-point-equation-lifting`.

The aggregate frontier now has both raw finite support and compact
case-status handoffs. A future worker needs the aggregate report to say that
each compact handoff still accepts, remains blocked, and still reports an open
case boundary. Without that rollup, the aggregate status can remain green while
one of the newer case-status surfaces drifts, closes, or changes its blocker.

The substitution graph correctness handoff needs one explicit exception: the
fixed-point construction case kind is `substitution-graph-correctness-proof`,
but the owning compact status blocker is `substitution-graph-correctness`.
The aggregate validator therefore must use an explicit construction-case to
blocker map rather than assuming the two identifiers are always equal.

## Decision

Extend `claims/fixed_point_construction_frontier_status.json` with a
`case_status_paths` map for the five compact construction-case status
manifests.

Update `autarkic_systems.fixed_point_construction_frontier_status` so the
aggregate validator imports and runs the owning compact status validators
instead of duplicating their internal logic. The aggregate report will expose a
`case_status_rollup` containing each construction case kind, compact status
path, acceptance result, frontier status, expected blocker, observed blocker,
construction case id, construction case status, failed subjects, and detail.

The rollup will fail closed when a required case-status path is missing,
unloadable, rejected by its owning validator, no longer `blocked`, blocked by
the wrong value for its construction case, no longer tied to the expected case
kind when the owning status exposes a construction case, or no longer
reporting `proof-case-open` where the owning status exposes an open-case
surface. For the substitution graph correctness aggregate handoff, the rollup
will validate the accepted `substitution-graph-correctness` blocker and the
handoff's own open correctness-case count while the existing ADR-0273
construction-case validation continues to enforce that the fixed-point
`substitution-graph-correctness-proof` case remains open.

The existing raw finite support behavior and non-claim boundary remain in
place. This ADR adds compact status-of-status validation only; it does not
prove or promote substitution representability, substitution graph
correctness, bridge equality, a fixed-point equation, an arithmetized proof
predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the aggregate manifest/module
  does not require or expose the five compact construction-case status paths.
- The checked-in aggregate frontier-status manifest validates.
- JSON output exposes a compact `case_status_rollup` with exactly five
  accepted compact case statuses and no failed subjects.
- Text output names the compact construction-case status rollup clearly.
- Missing case-status paths reject.
- Compact status blocker mismatches reject, including the
  `substitution-graph-correctness-proof` to `substitution-graph-correctness`
  blocker distinction.
- Closed or proof-promoted compact construction-case statuses reject.
- Unaccepted compact case statuses reject.
- Existing raw support-surface behavior, open construction-case checks, failed
  subjects, and non-claim boundaries remain intact.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_construction_frontier_status`.
- Green: `python -m unittest
  tests.test_fixed_point_construction_frontier_status
  tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.fixed_point_construction_frontier_status
  --format json`.
- Parse changed JSON files with `python -m json.tool`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check` and staged diff check before commit.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_construction_frontier_status
```

It ran 16 tests and failed with 9 errors and 1 failure because the aggregate
status did not yet expose the compact construction-case status rollup.
Representative failures were:

```text
AttributeError: 'FixedPointConstructionFrontierStatusManifest' object has no attribute 'case_status_paths'
AttributeError: 'FixedPointConstructionFrontierStatusReport' object has no attribute 'case_status_count'
KeyError: 'case_status_paths'
AssertionError: 'Compact construction-case status rollup: 5/5' not found
```

The implementation extends the aggregate manifest with `case_status_paths`,
imports and runs the five owning compact status validators, and exposes
`case_status_rollup` in the report, JSON payload, and text formatter. The
rollup checks that each compact case status accepts, remains `blocked`, is
blocked by the expected handoff blocker, and reports or inherits an open
construction-case boundary. The expected blocker map is explicit so
`substitution-graph-correctness-proof` rolls up the compact status blocked by
`substitution-graph-correctness`.

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_construction_frontier_status
python -m unittest tests.test_fixed_point_construction_frontier_status tests.test_suite_selection
python -c 'import json, subprocess, sys; completed = subprocess.run([sys.executable, "-m", "autarkic_systems.fixed_point_construction_frontier_status", "--format", "json"], cwd=".", capture_output=True, text=True, check=True); payload = json.loads(completed.stdout); assert payload["accepted"] is True; assert payload["frontier_status"] == "blocked"; assert payload["frontier_blocked_by"] == "fixed-point-construction"; assert payload["case_count"] == 5; assert payload["open_case_count"] == 5; assert payload["support_surface_count"] == 7; assert payload["case_status_count"] == 5; assert payload["accepted_case_status_count"] == 5; assert payload["failed_subjects"] == []; assert all(status["accepted"] for status in payload["case_status_rollup"]); assert all(status["frontier_status"] == "blocked" for status in payload["case_status_rollup"]); expected = {"diagonal-instance-closure": "diagonal-instance-closure", "substitution-representability-proof": "substitution-representability-proof", "substitution-graph-correctness-proof": "substitution-graph-correctness", "bridge-equality-proof": "bridge-equality-proof", "fixed-point-equation-lifting": "fixed-point-equation-lifting"}; assert {status["case_kind"]: status["frontier_blocked_by"] for status in payload["case_status_rollup"]} == expected; assert all(status["construction_case_status"] == "proof-case-open" for status in payload["case_status_rollup"]); print("aggregate json rollup accepted")'
python -m json.tool claims/fixed_point_construction_frontier_status.json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 16 tests passed;
- focused frontier-status plus suite-selection check: 21 tests passed;
- live JSON assertion printed `aggregate json rollup accepted`;
- changed JSON parsing passed;
- compileall and diff whitespace checks passed.

This slice preserves the original aggregate raw finite support-surface
behavior. It adds only a compact status-of-status handoff and does not prove
or promote substitution representability, substitution graph correctness,
bridge equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.
