# ADR-0237: Naive Fixed-Point Obstruction

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0235 records that the current naive quotation-substitution candidate is
not fixed. ADR-0236 makes that candidate a fail-closed dependency of the
formal-confidence target. The next useful step is to explain, with executable
evidence, why that naive scheme is structurally unable to close the
fixed-point construction blocker.

For the current template, direct substitution of a quoted token sequence into
the free code variable embeds the whole input sequence as nested
`sequence_cons` cells with unary numerals. That quotation surface grows with
both the number and magnitude of the input tokens. A real diagonal
construction must therefore move beyond direct term embedding of the code
sequence.

## Decision

Add a checked fixed-point obstruction surface that validates the length
growth for the current naive quotation-substitution candidate.

The obstruction will record the target candidate, the template context length,
the observed input length and token sum, and the resulting candidate length.
It will also validate the general length-growth equation for this one
template:

`candidate_length = context_length + 1 + 2 * input_length + token_sum`.

Since code tokens are natural numbers and the context length is non-negative,
the output length is strictly greater than the input length. Therefore the
current direct quotation-substitution operation cannot satisfy
`candidate_code = input_code`.

This does not prove a diagonal lemma, introduce arithmetic sequence axioms,
construct a fixed point, prove a fixed-point equation, add an arithmetized
proof predicate, change runtime behavior, change command semantics, add an
evidence bundle, or alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.fixed_point_obstruction` and
  `claims/fixed_point_obstructions.json` do not exist.
- The obstruction manifest names the ADR-0235 naive candidate and records the
  current length-growth facts.
- The validator checks the fixed-point equation candidate dependency, formal
  codebook dependency, Willard anchors, target variable occurrence count,
  template context length, observed input length, token sum, and observed
  candidate length.
- Text and JSON CLI modes expose that the naive candidate is impossible by
  length growth.
- Missing, stale, or overclaiming obstruction records reject with compact
  failed subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_fixed_point_obstruction
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point-obstruction text/JSON, live project-status
  summary, live handoff with `--refresh-remotes`, compileall, JSON checks,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The new obstruction surface validates
`AS-FIXED-POINT-SELFCONS1-NAIVE-LENGTH-OBSTRUCTION` against the ADR-0235
candidate and formal codebook. The live report computes context length `5`,
input length `7`, input token sum `101`, quotation-term code length `116`,
candidate length `121`, and minimum growth delta `6`.

This converted the naive candidate's failure from a single observed mismatch
into a checked structural obstruction: direct quotation-term embedding
strictly grows the code sequence, so this scheme cannot satisfy
`candidate_code = input_code`. Focused validation passed 99 tests, and live
text/JSON CLI modes exposed the obstruction while preserving the
fixed-point-construction blocker.
