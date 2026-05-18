# ADR-0241: Substitution-Code Term Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0237 showed that the naive direct route to a fixed point is
length-obstructed: embedding a full quotation-term sequence directly inside
the target sentence strictly grows the candidate.

The diagonal lemma does not proceed by raw self-embedding. It needs an
arithmetized substitution function: a term that can denote the code produced by
substituting a code/numeral into a formula code. AS has capture-avoiding
meta-level substitution over nodes, but its formal arithmetic/codebook surface
does not yet have a term constructor for that arithmetized substitution-code
operation.

## Decision

Add a syntax-only `substitution_code(t,u)` term surface. The formal arithmetic
language names the symbol, the formal codebook assigns it a deterministic tag,
and the substitution helper treats it as a binary term for free-variable
calculation and node substitution.

This is a coding hook for later diagonal construction. It does not define the
arithmetic graph of substitution, prove representability, prove the diagonal
lemma, prove a fixed-point equation, construct a self-consistency sentence,
change runtime behavior, change command semantics, add an evidence bundle, or
alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because `substitution_code` is absent
  from the arithmetic language, codebook, encoder/decoder, and substitution
  traversal.
- `language/formal_arithmetic_language.json` names `substitution_code(t,u)` as
  a binary coding term without asserting arithmetic totality.
- `language/formal_codebook.json` assigns the term tag `18` and includes a
  checked `substitution_code(n,n)` round-trip example.
- `autarkic_systems.formal_code` encodes and decodes the term.
- `autarkic_systems.formal_substitution` calculates free variables and
  substitutes inside both term arguments.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_arithmetic_language
  tests.test_formal_code_encoding tests.test_formal_substitution`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-arithmetic/codebook/substitution text/JSON,
  live project-status summary, compileall, JSON checks, `git diff --check`,
  and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The formal arithmetic language now names `subst_code(t,u)` as a binary coding
term. The formal codebook assigns `substitution_code` tag `18`, round-trips the
checked `substitution_code(n,n)` example as `[18, 11, 4, 11, 4]`, and exposes
six checked examples. The substitution helper treats the term as a binary term
for free-variable calculation, substitution, and replacement validation.

Focused validation first failed for the missing symbol/tag/encoder/substitution
support, then passed 46 tests after implementation. The fixed-point frontier is
still blocked on representability and the actual diagonal construction; this
ADR only adds the syntactic term needed to state that route.
