# ADR-0242: Diagonal Seed Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0241 added the `substitution_code(t,u)` term needed to state the
diagonal-construction route. The fixed-point frontier still lacked an
executable artifact that uses that term in the way the diagonal lemma needs.

The current naive fixed-point candidate remains length-obstructed because it
directly embeds a full quotation-term sequence. The next honest step is to
check the syntactic seed `A(n)` where the target variable is replaced by
`substitution_code(n,n)`, then check the quoted seed instance
`A(quote(code(A)))`. This does not prove representability, but it moves the
frontier from raw self-embedding toward the arithmetized substitution route.

## Decision

Add `claims/diagonal_construction_targets.json` and
`autarkic_systems.diagonal_construction`.

The validator builds the diagonal seed from the existing fixed-point target,
encodes it through the formal codebook, quotes the seed code as a term, builds
the closed seed instance, and checks the recorded code/free-variable facts.

This does not prove that `substitution_code` represents meta-level
substitution, prove the diagonal lemma, prove a fixed-point equation, implement
an arithmetized proof predicate, claim self-consistency, change runtime
behavior, change command semantics, add an evidence bundle, or alter GitHub
submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.diagonal_construction` and
  `claims/diagonal_construction_targets.json` do not exist.
- The manifest records one diagonal seed for
  `AS-FIXED-POINT-SELFCONS1-TARGET`.
- The seed code is checked as `[41, 1, 22, 11, 1, 18, 11, 4, 11, 4]` with free
  variable `n`.
- The quoted seed instance is checked as closed, with code length `296` and
  prefix `[41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13]`.
- Missing targets, stale seed facts, and proved-status overclaims fail closed.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_diagonal_construction`.
- Green: the same focused suite passes after implementation.
- Regression: run live diagonal-construction text/JSON, live project-status
  summary, compileall, JSON checks, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest and validator check
`AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED`. The helper
`build_diagonal_seed_node` constructs the seed by replacing the fixed-point
target variable with `substitution_code(n,n)`. The helper
`build_diagonal_instance_code` quotes the seed code and builds the closed seed
instance. The live expected seed code has length `10`; the live quoted
instance has length `296`.

Focused validation first failed on the missing module, then passed 13 tests
after implementation. The fixed-point frontier remains blocked on
substitution representability, diagonal lemma proof, fixed-point equation
proof, and self-consistency theorem.
