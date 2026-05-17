# ADR-0010: Proof Apparatus Options

Date: 2026-05-17

Status: Accepted

## Context

AFS-R3 requires AS to choose and document a proof/refutation apparatus before
implementing proof-side machinery. The current AS code already names substrate
transition claims, but those claims do not yet have proof objects or a proof
checker.

The reviewed sources create three plausible directions:

- public Proflog and Fitting-style semantic tableaux;
- LeanTAP/alphaLeanTAP as a compact transparent tableaux reference;
- a deliberately tiny AS-local checker for the current claim surface.

## Decision

Use a minimal AS-local proof-certificate checker as the first apparatus
direction. Defer Proflog as the long-term SJAS-aligned tableaux path until the
active ADR-006x frontier is recovered or replaced. Use LeanTAP as a design
reference, not as the first dependency.

Record the detailed comparison in `docs/proof-apparatus-options.md`.

## Success Criteria

- The option note compares Proflog/Fitting, LeanTAP, and a minimal local
  checker against AS needs.
- The decision clearly states what AS will implement next and what it will not
  claim.
- The source manifest and literature map include the reviewed LeanTAP witness.
- The roadmap and open-problem register no longer leave P3 as an undecided
  apparatus question.

## Consequences

- ADR-0011 should define proof-certificate syntax and tests before any
  proof-checker code is added.
- AS can keep making local, testable progress without depending on missing
  Proflog material.
- The Proflog gap remains important; it is not erased by choosing a small local
  first apparatus.

## After Action Report

Accepted after reviewing:

- public Proflog source at `/home/sean/Projects/_upstream/proflog/proflog.scm`;
- SJAS Proflog boundary notes in `/home/sean/Projects/_upstream/sjas/nachlass/LOG.md`;
- ISLA notes in `/home/sean/Projects/_upstream/sjas/code/isla/notes.txt`;
- LeanTAP source at `/home/sean/Projects/_upstream/leanTAP`.

Verification:

- `python -m unittest discover` passed 30 tests.
- `jq -e . sources/manifest.json` passed.
- `jq -e . claims/transition_claims.json` passed.
- `git diff --check` passed.

Coverage limits:

- This ADR makes a direction choice only. It does not add a proof checker,
  theorem prover, or proof-object schema.
- The decision does not settle the long-term Proflog recovery question.
