# ADR-0173: Memory Rule Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0133 introduced `predicate-result` proof-certificate steps for
`UC-FIXED-OUTPUT-PRESERVED`. ADR-0172 migrated
`UC-FIXED-CONSUMED-INPUT-CLEARED` to the same explicit rule. The next
foundational fixed-cell claim still relies on `manifest-example` proof steps,
which verify examples but leave the evaluated predicate implicit in the proof
object.

The smallest useful follow-on is to migrate `UC-FIXED-MEMORY-RULE` without
changing runtime behavior, transition claims, object-language schema, evidence
bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-FIXED-MEMORY-RULE` from `manifest-example` proof steps to
`predicate-result` proof steps that explicitly name `fixed_role_memory_rule`.

This extends explicit predicate-result coverage across the three foundational
fixed-cell predicates already represented in the transition claim manifest.

## Success Criteria

- Red tests fail before implementation because `UC-FIXED-MEMORY-RULE` still
  uses `manifest-example`.
- The memory-rule certificate has exactly two `predicate-result` steps.
- Both memory-rule steps name `fixed_role_memory_rule`.
- Proof-certificate text/JSON and aggregate project-status output report the
  memory-rule certificate as two `predicate-result` steps.
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
ran 91 tests and failed because the memory-rule certificate still used
`manifest-example`, and proof-certificate/project-status reports still rendered
the memory-rule certificate as two `manifest-example` steps.

The implementation migrated both `UC-FIXED-MEMORY-RULE` certificate steps to
`predicate-result` and named `fixed_role_memory_rule` directly on both steps.
No runtime behavior, transition claims, object-language rules, evidence
bundles, source-status records, or status schema versions changed.

The same focused suite then passed with 91 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the
updated certificate surface. JSON parsing for the touched certificate
manifest, `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 771 tests.
