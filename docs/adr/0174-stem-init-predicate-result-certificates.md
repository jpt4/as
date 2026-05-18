# ADR-0174: Stem-Init Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0133 introduced `predicate-result` proof-certificate steps for
`UC-FIXED-OUTPUT-PRESERVED`. ADR-0172 and ADR-0173 extended the same explicit
proof-object shape to consumed-input clearing and fixed-role memory behavior.
The remaining original fixed-cell predicate claim,
`UC-FIXED-STEM-INIT-RESET`, still uses `manifest-example` proof steps.

The next smallest proof-object hardening step is to migrate that certificate
without changing runtime behavior, transition claims, object-language schema,
evidence bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-FIXED-STEM-INIT-RESET` from `manifest-example` proof steps to
`predicate-result` proof steps that explicitly name `stem_init_resets_to_stem`.

This completes predicate-named proof-step coverage for the four original
fixed-cell transition predicates.

## Success Criteria

- Red tests fail before implementation because `UC-FIXED-STEM-INIT-RESET`
  still uses `manifest-example`.
- The stem-init certificate has exactly two `predicate-result` steps.
- Both stem-init steps name `stem_init_resets_to_stem`.
- Proof-certificate text/JSON and aggregate project-status output report the
  stem-init certificate as two `predicate-result` steps.
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
ran 92 tests and failed because the stem-init certificate still used
`manifest-example`, and proof-certificate/project-status reports still rendered
the stem-init certificate as two `manifest-example` steps.

The implementation migrated both `UC-FIXED-STEM-INIT-RESET` certificate steps
to `predicate-result` and named `stem_init_resets_to_stem` directly on both
steps. No runtime behavior, transition claims, object-language rules,
evidence bundles, source-status records, or status schema versions changed.

The same focused suite then passed with 92 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the
updated certificate surface. JSON parsing for the touched certificate
manifest, `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 772 tests.
