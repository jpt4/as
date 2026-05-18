# ADR-0172: Consumed-Input Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0133 added the `predicate-result` proof-certificate rule and migrated
`UC-FIXED-OUTPUT-PRESERVED` to that richer rule. The remaining transition
proof certificates still mostly use `manifest-example`, which verifies the
examples but leaves the predicate name implicit in the proof object.

P1 in `docs/open-problems.md` remains open: richer proof clauses are still
needed behind the transition claim IDs. The next low-risk step is to migrate
one more foundational fixed-cell claim to `predicate-result` without changing
runtime behavior, claim examples, object-language syntax, or proof-verifier
code.

## Decision

Migrate `UC-FIXED-CONSUMED-INPUT-CLEARED` from `manifest-example` proof steps
to `predicate-result` proof steps that explicitly name
`consumed_input_cleared`.

This ADR changes only proof-certificate data, tests, and documentation. It
does not change Universal Cell runtime behavior, transition claims, object
language schema, evidence bundles, source-status records, or project-status
schema versions.

## Success Criteria

- Red tests fail before implementation because
  `UC-FIXED-CONSUMED-INPUT-CLEARED` still uses `manifest-example`.
- The consumed-input certificate has exactly two `predicate-result` steps.
- Both steps name `consumed_input_cleared`.
- Proof-certificate text/JSON and aggregate project-status output report the
  consumed-input certificate as two `predicate-result` steps.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_proof_certificates tests.test_project_status_report`
  fails before the proof-certificate manifest update.
- Green: the same focused suite passes after updating
  `claims/proof_certificates.json` and expected status output.
- Regression: run JSON parsing for touched JSON, proof-certificate CLI JSON,
  project-status JSON, `compileall`, `git diff --check`, and the full default
  suite before commit.

## After Action Report

Implemented. The focused red run
`python -m unittest tests.test_proof_certificates tests.test_project_status_report`
ran 90 tests and failed because the consumed-input certificate still used
`manifest-example`, and proof-certificate/project-status reports still rendered
the consumed-input certificate as two `manifest-example` steps.

The implementation migrated both `UC-FIXED-CONSUMED-INPUT-CLEARED` certificate
steps to `predicate-result` and named `consumed_input_cleared` directly on both
steps. No runtime behavior, transition claims, object-language rules,
evidence bundles, source-status records, or status schema versions changed.

The same focused suite then passed with 90 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the
updated certificate surface. JSON parsing for the touched certificate
manifest, `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 770 tests.
