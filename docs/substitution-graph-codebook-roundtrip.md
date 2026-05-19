# Substitution Graph Codebook Roundtrip

Status: finite graph-domain roundtrip evidence, not a general proof,
2026-05-19.

ADR-0257 adds `claims/substitution_graph_codebook_roundtrip.json` and
`autarkic_systems/substitution_graph_codebook_roundtrip.py`. It derives the
code subjects currently exercised by the substitution graph formula candidate
and finite evaluation examples, then checks that each subject decodes through
`language/formal_codebook.json` and re-encodes to the same code sequence.

## Purpose

The first substitution graph correctness case asks for assurance that graph
domain codes round-trip through the checked codebook before decoded graph
inputs are trusted. This verifier makes the current finite domain explicit:

- formula-candidate formula code;
- formula-candidate closed witness instance code;
- formula-candidate evaluated output code;
- each finite evaluation formula code;
- each finite evaluation argument code; and
- each finite evaluation output code.

The current subject set contains 12 codes: three from the formula candidate
surface and nine from the finite evaluation surface.

## Run

```sh
python -m autarkic_systems.substitution_graph_codebook_roundtrip
python -m autarkic_systems.substitution_graph_codebook_roundtrip --format json
```

The validator checks that:

- the formal codebook, formula candidate, and finite evaluation dependencies
  remain accepted;
- the expected source kinds are covered;
- the derived subject count matches the manifest;
- every derived code decodes and re-encodes to the same sequence;
- future work and non-claims remain explicit; and
- stale subject counts fail closed.

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. It is finite executable evidence for the
codebook-roundtrip correctness case.
