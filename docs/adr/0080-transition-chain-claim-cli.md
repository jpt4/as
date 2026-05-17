# ADR-0080: Transition Chain Claim CLI

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0078 added the first transition-chain claim/proof surface. ADR-0079 added
an explicit object language for that surface. At this point the chain claim
stack can be validated through unit tests, but there is no direct
operator-facing command comparable to the evidence registry CLI.

AS agents and future automation should be able to validate the chain claim
surface without knowing which Python test module exercises it. The command
should check the same layers that matter for this small chain stack:

- chain language manifest validity;
- executable manifest-example evaluation;
- chain proof-certificate verification; and
- chain claim/certificate fit against the chain object language.

## Decision

Add a CLI to `autarkic_systems/chain_claims.py`:

```sh
python -m autarkic_systems.chain_claims \
  --claims claims/transition_chain_claims.json \
  --certificates claims/transition_chain_proof_certificates.json \
  --language language/transition_chain_claim_language.json
```

The command will support text and JSON output via `--format text|json`, use
the checked-in paths by default, and return exit code `0` only when all
validation subjects pass.

This ADR does not add new chain behavior, chain claims, or proof rules.

## Success Criteria

- Red tests fail before implementation because the chain-claim CLI/report
  functions are absent.
- The text report prints one `OK` or `FAIL` line for each validation subject.
- The JSON report records accepted status, language ID, claim count,
  certificate count, result count, and per-result records.
- The module command returns `0` for the checked-in chain claim surface.
- The command returns `1` and reports a failed subject when a certificate
  manifest is incomplete.
- Existing chain claim, chain language, and full repository tests remain green.

## Consequences

Transition-chain claims become operator-checkable outside the unit-test runner.
This keeps the new chain surface visible to agents without widening the
evidence registry or the single-transition claim language.

## Test Plan

- Red: `python -m unittest tests.test_transition_chain_claim_cli` fails before
  CLI/report functions exist.
- Green: the same focused test passes after adding CLI support.
- Regression: run chain claim/language tests, the actual CLI in text and JSON
  modes, and the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/chain_claims.py`, with focused tests in
`tests/test_transition_chain_claim_cli.py`.

The focused red run failed because the chain-claim CLI/report functions were
absent from `autarkic_systems.chain_claims`. The green implementation adds a
project-level validation report over four subjects:

- `chain-language-manifest`;
- `chain-examples`;
- `chain-certificates`; and
- `chain-surface`.

The command now supports the checked-in defaults:

```sh
python -m autarkic_systems.chain_claims
python -m autarkic_systems.chain_claims --format json
```

It returns `0` when all subjects pass and `1` when a subject fails, including
the tested incomplete-certificate case. The JSON payload records accepted
status, language ID, claim count, certificate count, result count, and
per-result records.

Verification passed:

- focused red:
  `python -m unittest tests.test_transition_chain_claim_cli` failed before
  CLI/report functions were added;
- focused green:
  `python -m unittest tests.test_transition_chain_claim_cli` passed 7 tests;
- adjacent chain CLI/language/claim stack passed 17 tests;
- actual chain CLI text mode passed;
- actual chain CLI JSON mode passed with `accepted: true`, `claim_count: 1`,
  and `certificate_count: 1`;
- `py_compile` passed for the touched module and focused test;
- `git diff --check` passed;
- `python -m unittest discover` passed 471 tests; and
- the evidence registry JSON CLI still reported `accepted: true` and
  `bundle_count: 8`.
