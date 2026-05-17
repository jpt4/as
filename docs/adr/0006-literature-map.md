# ADR-0006: Literature Map And Open Problems

Date: 2026-05-17

Status: Accepted

## Context

The AS prelude requires assessment and organization of existing literature.
ADR-0001 and ADR-0002 identified the subordinate repositories, but AS still
needs a project-owned map from sources to claims and from claims to open
problems.

The map must serve implementation, not bibliography for its own sake. It should
identify which sources constrain the current executable probes and which open
questions should generate future ADRs.

## Decision

Add:

- `docs/literature-map.md`: annotated first-pass map of primary and secondary
  sources by AS role.
- `docs/open-problems.md`: ranked open problems that can generate future ADRs.

Correct the roadmap numbering so the literature map is ADR-0006 rather than a
second ADR-0005.

## Success Criteria

- The map covers AS, AFS, PRC, SJAS, and adjacent Proflog/Fitting material.
- Each source entry says what it contributes to AS.
- Open problems are ranked by near-term leverage.
- The map identifies evidence gaps rather than implying the literature is
  complete.

## Consequences

- Future code slices can cite project-owned source roles instead of re-reading
  the whole subordinate tree.
- The next likely implementation direction is clearer: either expand the UC
  probe toward stem/reconfiguration semantics or add a tiny syntax/predicate
  claim manifest over the current transition predicates.

## After Action Report

Pending verification.
