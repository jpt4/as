# ADR-0176: Stem Buffer Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0175 migrated the first stem reconfiguration proof certificate to
`predicate-result`. The next transition certificate in the manifest,
`UC-STEM-BUFFER-ACCUMULATES`, still uses `manifest-example` proof steps even
though the underlying transition predicate is named directly in the object
language as `stem_buffer_accumulates`.

Stem buffer accumulation is the first standard-signal input accumulation
predicate. Migrating its certificate continues the proof-object hardening path
without changing runtime behavior, transition claims, object-language schema,
evidence bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-STEM-BUFFER-ACCUMULATES` from `manifest-example` proof steps to
`predicate-result` proof steps that explicitly name `stem_buffer_accumulates`.

## Success Criteria

- Red tests fail before implementation because `UC-STEM-BUFFER-ACCUMULATES`
  still uses `manifest-example`.
- The stem-buffer certificate has exactly four `predicate-result` steps.
- All stem-buffer steps name `stem_buffer_accumulates`.
- Proof-certificate text/JSON and aggregate project-status output report the
  stem-buffer certificate as four `predicate-result` steps.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_proof_certificates tests.test_project_status_report`
  fails before the proof-certificate manifest update.
- Green: the same focused suite passes after updating
  `claims/proof_certificates.json` and expected status output.
- Regression: run JSON parsing for touched JSON, proof-certificate CLI JSON,
  project-status JSON, object-language JSON, `compileall`, `git diff --check`,
  and the full default suite before commit.

## After Action Report

Implemented. The focused red run
`python -m unittest tests.test_proof_certificates tests.test_project_status_report`
ran 94 tests and failed because the stem-buffer certificate still used
`manifest-example`, and proof-certificate/project-status reports still rendered
the stem-buffer certificate as four `manifest-example` steps.

The implementation migrated all four `UC-STEM-BUFFER-ACCUMULATES` certificate
steps to `predicate-result` and named `stem_buffer_accumulates` directly on all
steps. No runtime behavior, transition claims, object-language rules,
evidence bundles, source-status records, or status schema versions changed.

The same focused suite then passed with 94 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the
updated certificate surface. JSON parsing for the touched certificate
manifest, `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 774 tests.
