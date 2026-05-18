# ADR-0246: Substitution Graph Target

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0244 checked one concrete meta-level substitution graph witness for the
current diagonal seed, and ADR-0245 made that witness visible to aggregate
formal-confidence validation. The next blocker named by that witness is a
formal delta0 graph formula for `substitution_code`.

It would be too strong to claim that formula now. The safe next step is to
record the exact target boundary for such a formula: relation name, graph
variables, required language features, witness tuple, and non-claims.

## Decision

Add `claims/substitution_graph_targets.json` and
`autarkic_systems.substitution_graph_target`.

The new surface validates one target:

- relation name `subst_code_graph`;
- formula class `delta0`;
- graph variables `x`, `y`, and `z` over the current formal arithmetic
  language;
- required language features for bounded delta0 graph work;
- the checked ADR-0244 witness tuple as the first concrete graph point; and
- explicit future work before representability can be claimed.

This records the formal obligation without constructing a delta0 formula,
proving formula correctness, proving substitution representability, proving a
diagonal lemma, proving a fixed-point equation, or claiming self-consistency.

This does not change aggregate formal-confidence validation yet, does not add
runtime behavior, does not change command semantics, does not add an evidence
bundle, and does not alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_graph_target` and
  `claims/substitution_graph_targets.json` do not exist.
- The manifest names `AS-SUBSTITUTION-GRAPH-DELTA0-TARGET`.
- The validator checks formal-language, codebook, and substitution-witness
  dependencies.
- The validator confirms that required language features are present and that
  graph variables are known formal-language variables.
- Healthy text and JSON reports expose the accepted target and observed
  witness output length `296`.
- Unknown witness IDs, stale witness facts, missing required language
  features, and constructed/proved statuses fail closed with specific failure
  subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_target`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph text/JSON, live project-status
  summary, compileall, JSON checks, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records `AS-SUBSTITUTION-GRAPH-DELTA0-TARGET` as
`graph-formula-target-not-constructed`. The validator loads the formal
arithmetic language, formal codebook, and substitution-representability
witness surface; checks the required delta0, bounded-quantifier, equality,
less-than, and `substitution_code` language features; and tethers the target
to the checked witness output length `296`.

Focused validation first failed because the module did not exist, then passed
12 tests after implementation. This names the formal graph-formula obligation
while preserving all proof-level blockers.
