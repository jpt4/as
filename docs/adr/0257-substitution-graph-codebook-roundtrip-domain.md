# ADR-0257: Substitution Graph Codebook Roundtrip Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0254 decomposed the substitution graph correctness target into open proof
cases. The first case requires confidence that graph-domain codes round-trip
through the checked formal codebook before decoded graph inputs are trusted.

The current codebook already validates examples, and the graph formula and
finite evaluation surfaces already exercise concrete graph-domain codes. Those
facts are not tied together as a fail-closed domain check for the correctness
case.

## Decision

Add `claims/substitution_graph_codebook_roundtrip.json` and
`autarkic_systems.substitution_graph_codebook_roundtrip`.

The verifier derives the current graph-domain code subjects from the checked
formula candidate and finite evaluation manifests, then verifies that every
derived code decodes through `language/formal_codebook.json` and re-encodes to
the same token sequence. It records subject counts and source-kind coverage as
finite executable evidence.

Make the `codebook-roundtrip` correctness case depend on this verifier via a
new `codebook_roundtrip_path` field in
`claims/substitution_graph_correctness_cases.json`.

This does not prove formula correctness, substitution representability, the
diagonal lemma, a fixed-point equation, or self-consistency. It is finite
domain evidence for the first open correctness case, not a general proof that
every possible code round-trips.

## Success Criteria

- Red tests fail before implementation because the roundtrip verifier and
  manifest do not exist, the correctness case manifest has no
  `codebook_roundtrip_path`, and the first case does not depend on
  `codebook_roundtrip`.
- The new verifier accepts the checked graph-domain subject set.
- The verifier derives 12 code subjects from the formula candidate and finite
  evaluation surfaces.
- Text and JSON output expose accepted roundtrip status and subject counts.
- Stale subject counts reject the verifier.
- The correctness-case validator fails closed over the new verifier and reports
  `codebook_roundtrip` as an accepted dependency on the healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_codebook_roundtrip
  tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live roundtrip text/JSON, live correctness-cases text/JSON,
  live formal-confidence text, live project-status summary, compileall,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/substitution_graph_codebook_roundtrip.py`,
`claims/substitution_graph_codebook_roundtrip.json`, and
`autarkic_systems/substitution_graph_correctness_cases.py`.

The red focused run failed before implementation because the roundtrip module
and manifest were absent, the correctness-case manifest had no
`codebook_roundtrip_path`, and the first correctness case still depended only
on `correctness_target` and `codebook`.

The green implementation derives 12 graph-domain code subjects: three from the
formula-candidate surface and nine from the finite evaluation surface. Each
subject decodes through the checked formal codebook and re-encodes to the same
token sequence. The correctness-case validator now loads the roundtrip
manifest and requires `codebook_roundtrip` for the `codebook-roundtrip` case.

Focused roundtrip and correctness-case tests passed 22 tests. This is finite
domain evidence only; it keeps all correctness cases open and does not prove
formula correctness, substitution representability, the diagonal lemma, a
fixed-point equation, or self-consistency.
