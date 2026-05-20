# ADR-0284: Substitution Graph Correctness Case Status Rollup

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0274 added an aggregate substitution graph correctness frontier status.
That surface loads `claims/substitution_graph_correctness_cases.json`, checks
the raw support artifacts named by the five correctness proof cases, and
preserves the aggregate `substitution-graph-correctness` blocker.

ADR-0279 through ADR-0283 then added compact per-case frontier status surfaces
for the same five proof cases:

- `codebook-roundtrip`;
- `quotation-term-closure`;
- `meta-substitution-semantics`;
- `formula-schema-relation`; and
- `diagonal-witness-composition`.

The aggregate frontier now has two related handoff layers. The older raw
support summary remains useful, but a future worker also needs one compact
place to confirm that each newer per-case status surface still accepts, remains
blocked by its own case kind, and still reports an open proof case. Without
that rollup, the aggregate status can accept while a more specific case-status
handoff has drifted.

## Decision

Extend `claims/substitution_graph_correctness_frontier_status.json` with a
`case_status_paths` map for the five compact case-status manifests added in
ADR-0279 through ADR-0283.

Update
`autarkic_systems.substitution_graph_correctness_frontier_status` so the
aggregate validator imports and runs the existing per-case status validators
rather than duplicating their internal logic. The aggregate report will expose
a `case_status_rollup` containing each case kind, compact status path,
acceptance result, frontier status, blocker, proof-case id, proof-case status,
and failed subjects.

The rollup will fail closed when a required case-status path is absent,
unloadable, not accepted by its owning validator, no longer `blocked`, blocked
by a value other than its case kind, no longer tied to the expected case kind,
or no longer reporting `proof-case-open`.

The existing raw support-surface and per-case support summaries remain in
place. This ADR adds handoff/status validation only; it does not promote any
proof case and does not claim formula correctness, substitution
representability, the diagonal lemma, a fixed-point equation, an arithmetized
proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the aggregate manifest/module
  does not require or expose the five compact case-status paths.
- The checked-in aggregate frontier-status manifest validates.
- JSON output exposes `case_status_rollup` with exactly five accepted compact
  case statuses and no failed subjects.
- Text output names the compact case-status rollup clearly.
- Missing case-status paths reject.
- Case-status blocker mismatches reject.
- Closed or proof-promoted case statuses reject.
- Unaccepted compact case statuses reject.
- Existing aggregate raw support-surface behavior, open-case checks, failed
  subjects, and non-claim boundaries remain intact.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_correctness_frontier_status`.
- Green: `python -m unittest
  tests.test_substitution_graph_correctness_frontier_status
  tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.substitution_graph_correctness_frontier_status
  --format json`.
- Parse changed JSON files with `python -m json.tool`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check` and staged diff check before commit.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status
```

It ran 17 tests and failed with 8 errors and 1 failure because the aggregate
status did not yet expose the compact case-status rollup. Representative
failures were:

```text
AttributeError: 'SubstitutionGraphCorrectnessFrontierStatusManifest' object has no attribute 'case_status_paths'
AttributeError: 'SubstitutionGraphCorrectnessFrontierStatusReport' object has no attribute 'case_status_count'
KeyError: 'case_status_paths'
AssertionError: 'Compact case-status rollup: 5/5' not found
```

The implementation extends the aggregate manifest with `case_status_paths`,
imports and runs the five compact case-status validators from ADR-0279 through
ADR-0283, and exposes `case_status_rollup` in the report, JSON payload, and
text formatter. The rollup checks that each compact case status accepts,
remains `blocked`, is blocked by its own case kind, and reports
`proof-case-open`.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status
python -m unittest tests.test_substitution_graph_correctness_frontier_status tests.test_suite_selection
python -m autarkic_systems.substitution_graph_correctness_frontier_status --format json | python -c 'import json,sys; p=json.load(sys.stdin); assert p["accepted"] is True; assert p["frontier_status"] == "blocked"; assert p["frontier_blocked_by"] == "substitution-graph-correctness"; assert p["case_count"] == 5; assert p["open_case_count"] == 5; assert p["support_surface_count"] == 11; assert p["case_status_count"] == 5; assert p["accepted_case_status_count"] == 5; assert p["failed_subjects"] == []; assert all(s["accepted"] for s in p["case_status_rollup"]); assert all(s["frontier_status"] == "blocked" for s in p["case_status_rollup"]); assert all(s["frontier_blocked_by"] == s["case_kind"] for s in p["case_status_rollup"]); assert all(s["proof_case_status"] == "proof-case-open" for s in p["case_status_rollup"]); print("aggregate json rollup accepted")'
python -m json.tool claims/substitution_graph_correctness_frontier_status.json >/dev/null
python -m autarkic_systems.substitution_graph_correctness_frontier_status
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 17 tests passed;
- focused frontier-status plus suite-selection check: 22 tests passed;
- live JSON assertion printed `aggregate json rollup accepted`;
- changed JSON parsing passed;
- live text CLI reported accepted status, five open cases, eleven support
  surfaces, `Compact case-status rollup: 5/5`, and no failed subjects;
- compileall and diff whitespace checks passed.

This slice preserves the original aggregate raw support-surface behavior. It
adds only a compact status-of-status handoff and does not prove or promote
formula correctness, substitution representability, the diagonal lemma, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
