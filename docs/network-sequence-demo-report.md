# Network Sequence Demo Report

ADR-0204 adds `autarkic_systems/network_sequence_demo.py`, a compact first-run
report for the checked post-handoff network-sequence evidence bundle.

## Purpose

The network-sequence work is intentionally split across claims, proof
certificates, object-language manifests, an executable witness, lower-level
chain evidence, source-status records, and an evidence bundle. That split is
good for audit, but it is awkward as a demo surface.

The network sequence demo report keeps the existing validator as the authority
and presents the current post-handoff sequence as one claim-to-evidence path.

## Run

```sh
python -m autarkic_systems.network_sequence_demo
python -m autarkic_systems.network_sequence_demo --format json
python -m autarkic_systems.network_sequence_demo --registry evidence/sequences/manifest.json
python -m autarkic_systems.network_sequence_demo --registry evidence/sequences/manifest.json --format json
```

For one bundle, the text report names:

- the network-sequence evidence bundle;
- the sequence claim;
- the predicate, positive example, sequence helper, and expected status;
- validation status, result count, and failed subjects;
- missing evidence paths, if any;
- the sequence claim, proof, language, validator, and witness artifacts;
- the underlying transition-chain evidence bundles;
- the source-status boundaries; and
- the explicit boundary terms.

JSON mode emits the same surface for automation. Every evidence layer includes
an `exists` flag, and the top-level `missing_evidence_paths` list summarizes
missing registered bundle paths or missing evidence-layer paths.

Registry mode validates `evidence/sequences/manifest.json`, builds a demo
report for every existing registered bundle, and summarizes registry ID, bundle
count, accepted and failed counts, missing paths, and per-bundle demo reports.

## Boundary

This is not a new simulator, proof checker, validation path, trace, or SVG
surface. It delegates validation to
`autarkic_systems.network_sequence_evidence_bundle` and exists only to make
the current vertical artifact legible from one command.
