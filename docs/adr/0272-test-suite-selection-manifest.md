# ADR-0272: Test Suite Selection Manifest

Date: 2026-05-20

## Status

Accepted.

## Context

The fixed-point campaign has accumulated useful executable regressions, but
some of those checks are no longer good default-suite citizens. They exercise
deep fixed-point validator chains and status surfaces that are important before
major revisions, yet slower than the ordinary feedback path needed while
editing unrelated proof, claim, or documentation slices.

The project rules already require slower regressions to be separated into an
explicit extended suite rather than placed on the default fast path. The
separation must be repo-native and fail closed: a stale suite list must not
silently omit new tests, and a stale extended module name must not quietly
produce a false sense of coverage.

## Decision

Add `tests/suite_manifest.json` and a stdlib-only selector module at
`autarkic_systems.test_suite_selection`.

The manifest defines two leaf suites:

- `fast`, computed from discovered `tests/test_*.py` modules minus explicit
  extended fixed-point regressions; and
- `extended-fixed-point`, an explicit list of all current fixed-point unittest
  modules plus the formal-confidence, project-status, handoff, and vertical-demo
  aggregate checks that traverse the same slow status stack.

The selector validates the manifest against live discovery before it lists or
runs anything. Every discovered test module must be classified exactly once
into a leaf suite. Every explicit module name must exist. The aggregate `all`
suite is the union of the leaf suites, not a separate hand-maintained list.

Expose:

- `python -m autarkic_systems.test_suite_selection --suite fast --list`;
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
  --list`;
- `python -m autarkic_systems.test_suite_selection --suite all --list`; and
- the same commands without `--list`, which run selected modules through
  `unittest`.

This is a test-selection surface only. It does not change proof validators,
claim manifests, mathematical semantics, or skip decorators on existing tests.

## Success Criteria

- Red tests fail before implementation because the selector module and suite
  manifest do not exist.
- The checked-in manifest includes schema/version/id fields, suite
  definitions, rationale, and non-goals.
- The extended fixed-point suite explicitly includes at least the current
  fixed-point/status regressions named by this ADR.
- The extended fixed-point suite also includes every currently discovered
  `tests.test_fixed_point_*` module, so new fixed-point regressions cannot slip
  into the fast path without an explicit manifest update.
- The selector discovers `tests/test_*.py` modules and validates that every
  discovered module is classified exactly once into `fast` or
  `extended-fixed-point`.
- Stale explicit module names fail closed.
- Leaf-suite overlap or omission fails closed.
- `fast` excludes the explicit extended fixed-point modules.
- `all` is the union of the two leaf suites.
- List mode prints the selected modules without running tests.
- Run mode loads selected modules through `unittest`.

## Test Plan

- Red: `python -m unittest tests.test_suite_selection`.
- Green: `python -m unittest tests.test_suite_selection`.
- Operator listing checks:
  - `python -m autarkic_systems.test_suite_selection --suite fast --list`;
  - `python -m autarkic_systems.test_suite_selection --suite
    extended-fixed-point --list`.
- Feasibility check: `python -m autarkic_systems.test_suite_selection --suite
  fast`.
- Hygiene: `python -m compileall autarkic_systems tests`, `jq -e .
  tests/suite_manifest.json`, and `git diff --check`.

## After Action Report

Red step captured before implementation:

```sh
python -m unittest tests.test_suite_selection
```

The focused suite failed with one import error because
`autarkic_systems.test_suite_selection` did not exist yet. This is the expected
red state for the selector/manifest slice.

Live verification of the initial minimal extended list completed but showed it
was too narrow for the intended default boundary: `--suite fast` still ran 133
modules and 1,185 tests in 927.401 seconds while spending substantial time in
other `tests.test_fixed_point_*` modules. The manifest was therefore tightened
to make the extended suite all current fixed-point unittest modules plus
`tests.test_formal_confidence_target` and `tests.test_project_status_report`.

A second fast verification attempt after that tightening was stopped during
`tests.test_vertical_demo_digest` after also running `tests.test_handoff_status`.
Those modules call the same slow aggregate status stack, so the extended suite
now also includes `tests.test_handoff_status` and
`tests.test_vertical_demo_digest`. Substitution-graph finite-domain tests remain
in the fast suite because they are formal-domain checks, not aggregate
status/handoff surfaces.

The final green verification commands were:

```sh
python -m unittest tests.test_suite_selection
python -m autarkic_systems.test_suite_selection --suite fast --list
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point --list
python -m autarkic_systems.test_suite_selection --suite fast
python -m compileall autarkic_systems tests
jq -e . tests/suite_manifest.json
git diff --check
```

Observed results:

- focused selector suite: 5 tests passed;
- fast list mode: 123 modules, excluding all current
  `tests.test_fixed_point_*` modules plus formal-confidence, project-status,
  handoff, and vertical-demo aggregate/status modules;
- extended-fixed-point list mode: 17 modules;
- final fast run: 1,081 tests passed in 82.044 seconds
  (`elapsed=82.358`);
- compileall, JSON parsing, and diff whitespace checks passed.

This selector is an operational testing surface only. It does not change proof
validators, claim manifests, mathematical semantics, or skip decorators on any
existing tests.
