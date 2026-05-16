# ADR-0003: Source Manifest

Date: 2026-05-16

Status: Accepted

## Context

AS is already drawing intent from multiple repositories. The initial subordinate
review covered AFS, PRC, and SJAS; the AFS requirement definition also found
that SJAS points to Proflog-adjacent implementation work. Without a pinned
manifest, future claims about what was reviewed or what executable frontier is
current will become ambiguous.

`AGENTS.md` also requires assessment and organization of existing literature
and executable artifacts wherever possible. A source manifest is the minimum
structured artifact needed before deeper literature and implementation work.

## Decision

Add:

- `sources/manifest.json`: a structured repository manifest with roles,
  relationships, local paths, default branches, reviewed commits, public remote
  heads, and status notes.
- `docs/source-manifest.md`: a human-readable explanation and verification
  commands.

Do not add a custom verifier yet. `jq` is available on this machine and is
sufficient for the first structural check.

## Success Criteria

- Every repository currently used by AS research is represented.
- The manifest distinguishes subordinate repositories from adjacent candidates.
- The manifest records public remote state separately from local AS state.
- The manifest is valid JSON.

## Consequences

- ADR-0004 can refer to a stable source baseline when selecting the first
  executable probe.
- The Proflog gap is now represented as source-state metadata instead of only
  prose in the AFS requirements.
- Future agents can refresh the manifest by checking local `rev-parse` and
  remote `ls-remote` output.

## After Action Report

The manifest was added for AS, AFS, PRC, SJAS, and Proflog. `jq -e
sources/manifest.json` is the required verification command for this slice.
