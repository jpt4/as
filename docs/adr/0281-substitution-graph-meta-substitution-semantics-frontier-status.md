# ADR-0281: Substitution Graph Meta-Substitution Semantics Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into open proof cases.
ADR-0259 then added finite meta-substitution semantic evidence for the
`meta-substitution-semantics` case, and ADR-0274 summarized the aggregate
substitution graph correctness frontier.

The meta-substitution-semantics case now needs the same compact handoff shape
as ADR-0279 and ADR-0280. A later worker should be able to see that the finite
support surface validates, the matching correctness case remains open, and the
frontier is still the general capture-avoiding substitution semantics proof.

## Decision

Add
`claims/substitution_graph_meta_substitution_semantics_frontier_status.json`
and
`autarkic_systems.substitution_graph_meta_substitution_semantics_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` manifest, locate the single
`meta-substitution-semantics` case, and require that case to remain
`proof-case-open`. It will also load
`claims/substitution_graph_meta_substitution_semantics.json`, run the existing
meta-substitution-semantics validator, require no failed subjects, and report
the finite support facts needed for handoff: six semantic subjects, source
kinds for formula candidates and finite evaluations, and the current formal
substitution and graph support paths.

This is a compact frontier/status surface only. It does not promote the
meta-substitution-semantics case and does not claim formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier
  and manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The manifest points to the current substitution graph correctness case map
  and meta-substitution-semantics support manifest.
- The matching correctness case has case kind `meta-substitution-semantics`
  and remains `proof-case-open`.
- The frontier remains `blocked` by `meta-substitution-semantics`.
- The case support subjects are exactly correctness target, formal
  substitution, and meta-substitution semantics.
- The meta-substitution-semantics support surface validates with no failed
  subjects and six semantic subjects.
- Text and JSON output expose accepted status, frontier status/blocker, the
  case id/kind/status, support surface count, support facts, and failed
  subjects.
- Proof-promotion statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed meta-substitution-semantics case rejects.
- Case dependency drift rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_meta_substitution_semantics_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite together with
  `tests.test_suite_selection`, parse the new JSON manifest, run the live text
  and JSON CLIs, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_meta_substitution_semantics_frontier_status
```

It reported the missing ADR-0281 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'substitution_graph_meta_substitution_semantics_frontier_status' from 'autarkic_systems'
```

The implementation added the compact meta-substitution-semantics frontier
manifest, verifier, CLI, documentation, and focused tests. The surface loads
the existing substitution graph correctness case map, requires
`AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS` to remain
`proof-case-open`, runs the existing meta-substitution-semantics support
validator, and reports the finite semantics support as accepted with six
semantic subjects and no failed subjects.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_meta_substitution_semantics_frontier_status
python -m unittest tests.test_suite_selection tests.test_substitution_graph_meta_substitution_semantics_frontier_status
python -m json.tool claims/substitution_graph_meta_substitution_semantics_frontier_status.json
python -m autarkic_systems.substitution_graph_meta_substitution_semantics_frontier_status
python -m autarkic_systems.substitution_graph_meta_substitution_semantics_frontier_status --format json | python -c 'import json,sys; p=json.load(sys.stdin); assert p["accepted"] is True; assert p["frontier_status"] == "blocked"; assert p["frontier_blocked_by"] == "meta-substitution-semantics"; assert p["proof_case"]["case_kind"] == "meta-substitution-semantics"; assert p["proof_case"]["status"] == "proof-case-open"; assert p["support_surface_count"] == 1; assert p["semantics_subject_count"] == 6; assert p["failed_subjects"] == []'
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 15 tests passed;
- focused suite plus suite-selection check: 20 tests passed;
- manifest JSON parsing passed;
- live text CLI: accepted, blocked by `meta-substitution-semantics`,
  `AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS` remained
  `proof-case-open`, one support surface accepted, six semantic subjects, and
  no failed subjects;
- live JSON CLI exposed `accepted: true`, `frontier_status: blocked`, one
  support surface, `semantics_subject_count: 6`, and an empty
  `failed_subjects` list;
- compileall and diff whitespace checks passed.

This slice adds a compact frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
