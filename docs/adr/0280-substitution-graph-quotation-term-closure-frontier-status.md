# ADR-0280: Substitution Graph Quotation Term Closure Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into open proof cases.
ADR-0258 then added finite quotation-term closure evidence for the
`quotation-term-closure` case, and ADR-0274 summarized the aggregate
substitution graph correctness frontier.

The quotation-term-closure case now needs its own compact handoff. A later
worker should be able to see that the finite support surface validates, the
matching correctness case remains open, and the next frontier is still a proof
of the general quotation closure property rather than a proved correctness
claim.

## Decision

Add
`claims/substitution_graph_quotation_term_closure_frontier_status.json` and
`autarkic_systems.substitution_graph_quotation_term_closure_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` manifest, locate the single
`quotation-term-closure` case, and require that case to remain
`proof-case-open`. It will also load
`claims/substitution_graph_quotation_term_closure.json`, run the existing
quotation-term-closure validator, require no failed subjects, and report the
finite support facts needed for handoff: twelve closure subjects, source kinds
for formula candidates and finite evaluations, and the current codebook and
quotation-term support paths.

This is a compact frontier/status surface only. It does not promote the
quotation-term-closure case and does not claim formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier
  and manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The manifest points to the current substitution graph correctness case map
  and quotation-term-closure support manifest.
- The matching correctness case has case kind `quotation-term-closure` and
  remains `proof-case-open`.
- The frontier remains `blocked` by `quotation-term-closure`.
- The case support subjects are exactly correctness target, codebook,
  quotation term, and quotation term closure.
- The quotation-term-closure support surface validates with no failed subjects
  and twelve closure subjects.
- Text and JSON output expose accepted status, frontier status/blocker, the
  case id/kind/status, support surface count, support facts, and failed
  subjects.
- Proof-promotion statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed quotation-term-closure case rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_quotation_term_closure_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite together with
  `tests.test_suite_selection`, parse the new JSON manifest, run the live text
  and JSON CLIs, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_quotation_term_closure_frontier_status
```

It reported the missing ADR-0280 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'substitution_graph_quotation_term_closure_frontier_status' from 'autarkic_systems'
```

The implementation added the compact quotation-term-closure frontier manifest,
verifier, CLI, documentation, and focused tests. The surface loads the existing
substitution graph correctness case map, requires
`AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE` to remain
`proof-case-open`, runs the existing quotation-term-closure support validator,
and reports the finite closure support as accepted with twelve closure
subjects and no failed subjects.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_quotation_term_closure_frontier_status
python -m unittest tests.test_suite_selection tests.test_substitution_graph_quotation_term_closure_frontier_status
python -m json.tool claims/substitution_graph_quotation_term_closure_frontier_status.json
python -m autarkic_systems.substitution_graph_quotation_term_closure_frontier_status
python -m autarkic_systems.substitution_graph_quotation_term_closure_frontier_status --format json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 14 tests passed;
- focused suite plus suite-selection check: 19 tests passed;
- manifest JSON parsing passed;
- live text CLI: accepted, blocked by `quotation-term-closure`,
  `AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE` remained
  `proof-case-open`, one support surface accepted, twelve closure subjects,
  and no failed subjects;
- live JSON CLI exposed `accepted: true`, `frontier_status: blocked`, one
  support surface, `subject_count: 12`, and an empty `failed_subjects` list;
- compileall and diff whitespace checks passed.

This slice adds a compact frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
