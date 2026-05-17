# ADR-0023: Stem Buffer Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0022 added the first standard-signal stem buffer behavior to the executable
Universal Cell probe. The behavior is now tested as code, but it is not yet a
named AS claim. Earlier transition behaviors were promoted into
`claims/transition_claims.json`, checked by predicates, and covered by
manifest-example proof certificates. The new stem buffer subset should receive
the same treatment before later command decoding builds on it.

The claim must stay narrow. ADR-0022 explicitly stops before five-bit command
interpretation, neighbor-target delivery, or dynamic reconfiguration. The claim
therefore covers only control-rail selection, 1/0 accumulation, full-buffer
boundary preservation, and malformed-input rejection.

## Decision

Add a named predicate and manifest claim for stem buffer accumulation:

- `stem_buffer_accumulates` in `autarkic_systems/transition_predicates.py`
  checks the ADR-0022 stem-buffer statuses and state changes;
- `claims/transition_claims.json` gains `UC-STEM-BUFFER-ACCUMULATES` with
  positive and negative executable examples;
- `claims/proof_certificates.json` gains a manifest-example certificate for
  the new claim;
- `language/transition_claim_language.json` gains the new predicate symbol;
- tests cover the predicate, claim manifest, proof certificate surface, and
  object-language surface.

## Success Criteria

- Red tests fail before implementation because `stem_buffer_accumulates` is
  absent.
- The predicate accepts control selection, matching append, non-matching append,
  full-buffer boundary preservation, and malformed-input rejection.
- The predicate rejects wrong appended bits and uncleared consumed input.
- The claim manifest has positive and negative examples that evaluate to the
  recorded expectations.
- The proof-certificate manifest covers the new claim.
- The object-language manifest recognizes the new predicate symbol.

## Consequences

- ADR-0022's behavior becomes part of the named AS claim surface.
- Later stem command-decoding work can depend on an explicit accumulation claim
  rather than raw transition tests only.
- Full command decoding and target routing remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_transition_predicates` failed with
  `ImportError: cannot import name 'stem_buffer_accumulates'` from
  `autarkic_systems.transition_predicates`.

Green step:

- Added `stem_buffer_accumulates`.
- Added `UC-STEM-BUFFER-ACCUMULATES` to `claims/transition_claims.json`.
- Added a `manifest-example` proof certificate for the new claim.
- Added `stem_buffer_accumulates` to the object-language predicate vocabulary.
- Added `docs/stem-buffer-claim.md`.

Full verification:

- `python -m unittest tests.test_transition_predicates
  tests.test_claim_manifest tests.test_proof_certificates
  tests.test_object_language` passed 31 tests.
- `python -m unittest discover` passed 109 tests.
- `python -m py_compile autarkic_systems/transition_predicates.py
  tests/test_transition_predicates.py` passed.
- `jq -e . claims/transition_claims.json claims/proof_certificates.json
  language/transition_claim_language.json` passed.
- `git diff --check` passed.

Coverage limits:

- This adds a claim for buffer accumulation only.
- It does not claim five-bit command interpretation.
- It does not add a schematic trace for buffer accumulation.
