# ADR-0137: Chain Object Language CLI

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0136 made the base transition object-language layer directly inspectable
through `python -m autarkic_systems.object_language`. The transition-chain
claim surface already has `python -m autarkic_systems.chain_claims`, but that
command reports summarized language/example/certificate/surface checks.

The chain object-language module itself still exposes only library validators.
That makes individual syntax-class and chain-surface failures harder to inspect
than the base transition language after ADR-0136.

## Decision

Add a `python -m autarkic_systems.chain_object_language` command.

The command will accept:

- `--language`, defaulting to `language/transition_chain_claim_language.json`;
- `--claims`, defaulting to `claims/transition_chain_claims.json`;
- `--certificates`, defaulting to
  `claims/transition_chain_proof_certificates.json`; and
- `--format text|json`, defaulting to `text`.

Text output will list all chain language-manifest and chain-claim-surface
validation results. JSON output will expose accepted state, language ID, claim
count, certificate count, result count, and per-result validation details. The
command will return `0` only when every language and surface validation result
is accepted.

## Success Criteria

- Red tests fail before implementation because the chain object-language module
  has no CLI helpers and module execution emits no chain language report.
- The checked-in chain object-language surface returns exit code `0` in text
  and JSON modes.
- A malformed chain language manifest returns exit code `1` and reports the
  failing syntax-class or surface detail.
- Module execution through `python -m autarkic_systems.chain_object_language`
  works in text and JSON modes.
- Full repository tests remain green.

## Consequences

The chain object-language layer gains the same direct diagnostic affordance as
the base transition object-language layer. Operators can inspect individual
chain syntax-class failures without going through the summarized chain-claim
CLI.

This CLI does not broaden the chain language or add runtime behavior.

## Test Plan

- Red: add direct-run and subprocess tests for text output, JSON output, and a
  failing chain language manifest.
- Green: add report construction, text/JSON formatting, CLI argument parsing,
  and `__main__` execution to `autarkic_systems.chain_object_language`.
- Regression: run focused chain object-language tests, JSON formatting,
  `py_compile`, `git diff --check`, and the full default test suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/chain_object_language.py` with focused tests
in `tests/test_chain_object_language.py`.

The red test run executed 12 chain object-language tests and failed because
the module had no project report, CLI runner, or `python -m` output. The green
implementation adds a `TransitionChainClaimLanguageProjectReport`, text and
JSON formatters, `--language` / `--claims` / `--certificates` overrides,
accepted/rejected exit codes, and module execution.

The checked-in chain language surface reports `accepted: true`,
`language_id: as-transition-chain-claim-v1`, `claim_count: 2`,
`certificate_count: 2`, and `result_count: 32` in JSON mode. A manifest
missing the `chain_formulae` syntax class returns exit code `1` and reports
`FAIL chain_formulae: missing syntax class: chain_formulae`.

Verification passed: focused chain object-language tests ran 12 tests;
`python -m autarkic_systems.chain_object_language` text and JSON output were
accepted; JSON formatting, `py_compile`, and `git diff --check` passed; and
`python -m unittest discover` passed 631 tests.
