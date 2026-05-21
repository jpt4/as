# ADR-0293: Test Suite Selection JSON List

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0272 added a fail-closed unittest suite selector with human-readable list
mode. Operators can already inspect the `fast`, `extended-fixed-point`, and
`all` suite boundaries without running tests, but automation still has to parse
text lines such as `manifest: ...`, `suite: ...`, `module_count: ...`, and
`- tests.test_...`.

End-of-month reporting and future agents need a stable, machine-readable list
surface that reflects the same validated suite plan as text list mode. The JSON
surface must not become a second selector, change suite membership, or affect
the normal unittest run path.

## Decision

Add a `--format` option to `autarkic_systems.test_suite_selection` list mode.
The default remains `text`, preserving ADR-0272 behavior:

```sh
python -m autarkic_systems.test_suite_selection --suite fast --list
```

JSON list mode is requested explicitly:

```sh
python -m autarkic_systems.test_suite_selection --suite fast --list --format json
```

The JSON payload is derived from the already validated `SuitePlan` and includes
at least:

- `manifest_id`;
- `manifest_schema_version`;
- `suite`;
- `module_count`;
- `modules`;
- `discovered_module_count`; and
- `command`, the exact `unittest` command implied by the selected modules.

The option is list-only in effect. Run mode keeps its existing behavior and
continues to load selected modules through stdlib `unittest`. Text list mode
keeps its line-oriented output so existing operator habits and documentation do
not break.

## Success Criteria

- Red tests fail before implementation because list mode has no
  `--format json` support.
- `python -m autarkic_systems.test_suite_selection --suite fast --list
  --format json` emits valid JSON.
- JSON output includes the manifest id/version, suite name, module count,
  selected module list, discovered module count, and the selected `unittest`
  command metadata.
- JSON output is covered for `fast` and `extended-fixed-point`.
- Text list behavior remains unchanged.
- Running selected suites remains unchanged.
- The change does not modify suite membership, proof validators, claim
  manifests, mathematical semantics, or skip decorators.

## Failure Criteria

- Existing text list consumers see changed line labels or module bullet format.
- Run mode starts emitting JSON, stops loading modules through `unittest`, or
  changes exit-code behavior.
- The JSON list payload can be produced without passing the manifest/discovery
  fail-closed checks.
- The JSON payload reorders or filters modules differently from text list mode.

## Test Plan

- Red:
  `python -m unittest tests.test_suite_selection.TestSuiteSelectionTests.test_json_list_mode_emits_fast_suite_plan tests.test_suite_selection.TestSuiteSelectionTests.test_json_list_mode_emits_extended_suite_plan`.
- Green: `python -m unittest tests.test_suite_selection`.
- Live JSON smokes:
  - `python -m autarkic_systems.test_suite_selection --suite fast --list
    --format json`;
  - `python -m autarkic_systems.test_suite_selection --suite
    extended-fixed-point --list --format json`.
- Text compatibility smoke:
  `python -m autarkic_systems.test_suite_selection --suite fast --list`.
- Hygiene: `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_suite_selection.TestSuiteSelectionTests.test_json_list_mode_emits_fast_suite_plan tests.test_suite_selection.TestSuiteSelectionTests.test_json_list_mode_emits_extended_suite_plan
```

It failed before implementation with two expected `SystemExit: 2` errors
because argparse did not recognize `--format json`:

```text
error: unrecognized arguments: --format json
Ran 2 tests in 0.005s
FAILED (errors=2)
```

After main advanced to `db2b4fa`, this branch was rebased with
`git rebase --autostash origin/main` before final verification. No ADR-0292
files were edited in this lane.

The implementation stayed in `autarkic_systems.test_suite_selection`. It adds
`manifest_schema_version` to `SuitePlan`, derives a JSON list payload from the
already validated plan, exposes `--format text|json`, and routes only list mode
through the new JSON formatter. Text list mode remains the default and run mode
still loads selected modules through stdlib `unittest`.

Focused verification on the rebased branch passed:

```sh
python -m unittest tests.test_suite_selection
```

Observed result:

```text
Ran 8 tests in 0.061s
OK
```

The live JSON list smokes ran on the rebased branch:

```sh
python -m autarkic_systems.test_suite_selection --suite fast --list --format json
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point --list --format json
```

The parsed payload summaries were:

```text
fast: manifest=as-test-suite-selection-v1 schema=1 modules=129 discovered=151 command_modules=129
extended-fixed-point: manifest=as-test-suite-selection-v1 schema=1 modules=22 discovered=151 command_modules=22
```

The live text compatibility smoke:

```sh
python -m autarkic_systems.test_suite_selection --suite fast --list
```

kept the ADR-0272 opening lines:

```text
manifest: as-test-suite-selection-v1
suite: fast
module_count: 129
modules:
- tests.test_asmsim_process_buffer_status
```

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

The fast suite reported manifest `as-test-suite-selection-v1`, suite `fast`,
129 selected modules, and 1176 tests passed in 305.396s.

This is a suite-list serialization change only. It does not change suite
membership, run-mode selection, proof validators, claim manifests, mathematical
semantics, GitHub submission/handoff freshness semantics from ADR-0292, or
existing skip decorators.
